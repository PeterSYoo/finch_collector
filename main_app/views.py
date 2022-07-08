from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid
import boto3
from .models import Finch, Seed, Photo
from .forms import FeedingForm, SignUpForm

# session = boto3.Session(profile_name='finchcollector') 

S3_BASE_URL = 'https://s3.us-west-1.amazonaws.com/'
BUCKET = 'finchcollector-py'

# Create your views here.
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

@login_required
def finches_index(request):
  # finches = Finch.objects.all()
  finches = Finch.objects.filter(user=request.user)
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

# def signup(request):
#   error_message = ''
#   if request.method == 'POST':
#     # This is how to create a 'user' form object
#     # that includes the data from the browser
#     form = UserCreationForm(request.POST)
#     if form.is_valid():
#       # This will add the user to the database
#       user = form.save()
#       # This is how we log a user in via code
#       login(request, user)
#       return redirect('index')
#     else:
#       error_message = 'Invalid sign up - try again'
#   # A bad POST or a GET request, so render signup.html with an empty form
#   form = UserCreationForm()
#   context = {'form': form, 'error_message': error_message}
#   return render(request, 'registration/signup.html', context)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  form = SignUpForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

class FinchCreate(LoginRequiredMixin, CreateView):
  model = Finch
  fields = ['name', 'breed', 'description', 'age']
  success_url = '/finches/'

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class FinchUpdate(LoginRequiredMixin, UpdateView):
  model = Finch
  # Let's disallow the renaming of a Finch by excluding the name field!
  fields = ['breed', 'description', 'age']

class FinchDelete(LoginRequiredMixin, DeleteView):
  model = Finch
  success_url = '/finches/'

class SeedList(LoginRequiredMixin, ListView):
  model = Seed
  template_name = 'seeds/index.html'

class SeedDetail(LoginRequiredMixin, DetailView):
  model = Seed
  template_name = 'seeds/detail.html'

class SeedCreate(LoginRequiredMixin, CreateView):
  model = Seed
  fields = ['name']

class SeedUpdate(LoginRequiredMixin, UpdateView):
  model = Seed
  fields = ['name']

class SeedDelete(LoginRequiredMixin, DeleteView):
  model = Seed
  success_url = '/seeds/'
