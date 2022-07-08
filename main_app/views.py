from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
import uuid
import boto3
from .models import Finch, Seed, Photo
from .forms import FeedingForm

S3_BASE_URL = 'https://s3.us-west-1.amazonaws.com/'
BUCKET = 'finchcollector-py'

# Create your views here.
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def finches_index(request):
  finches = Finch.objects.all()
  return render(request, 'finches/index.html', { 'finches': finches })

def finches_detail(request, finch_id):
  finch = Finch.objects.get(id=finch_id)
  # Get the seeds the finch doesn't have
  seeds_finch_doesnt_have = Seed.objects.exclude(id__in = finch.seeds.all().values_list('id'))
  feeding_form = FeedingForm()
  return render(request, 'finches/detail.html', {
    'finch': finch, 'feeding_form': feeding_form,
    # Add the seeds to be displayed
    'seeds': seeds_finch_doesnt_have
  })

def add_feeding(request, finch_id):
  # create the ModelForm using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the finch_id assigned
    new_feeding = form.save(commit=False)
    new_feeding.finch_id = finch_id
    new_feeding.save()
  return redirect('detail', finch_id=finch_id)

def assoc_seed(request, finch_id, seed_id):
  # Note that you can pass a seed's id instead of the whole object
  Finch.objects.get(id=finch_id).seeds.add(seed_id)
  return redirect('detail', finch_id=finch_id)

def add_photo(request, finch_id):
  # photo-file will be the "name" attribute on the <input type="file">
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    # need a unique "key" for S3 / needs image file extension too
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    # just in case something goes wrong
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      # build the full url string
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      # we can assign to finch_id or finch (if you have a finch object)
      photo = Photo(url=url, finch_id=finch_id)
      photo.save()
    except:
      print('An error occurred uploading file to S3')
      return redirect('detail', finch_id=finch_id)
  return redirect('detail', finch_id=finch_id)

class FinchCreate(CreateView):
  model = Finch
  fields = '__all__'
  success_url = '/finches/'

class FinchUpdate(UpdateView):
  model = Finch
  # Let's disallow the renaming of a Finch by excluding the name field!
  fields = ['breed', 'description', 'age']

class FinchDelete(DeleteView):
  model = Finch
  success_url = '/finches/'

class SeedList(ListView):
  model = Seed
  template_name = 'seeds/index.html'

class SeedDetail(DetailView):
  model = Seed
  template_name = 'seeds/detail.html'

class SeedCreate(CreateView):
  model = Seed
  fields = ['name']

class SeedUpdate(UpdateView):
  model = Seed
  fields = ['name']

class SeedDelete(DeleteView):
  model = Seed
  success_url = '/seeds/'
