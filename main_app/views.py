from django.shortcuts import render
from django.http import HttpResponse

class Finches:  # Note that parens are optional if not inheriting from another class
  def __init__(self, name, breed, description, age):
    self.name = name
    self.breed = breed
    self.description = description
    self.age = age

finches = [
  Finches('Mask', 'American Goldfinch', 'loves sunflowers and nujer', 1),
  Finches('Hot Cheeto', 'Cassia Crossbill', 'dangles from cones', 0),
  Finches('Mustang', 'Evening Grosbeak', 'prefers platform feeders', 2),
]

# Create your views here.
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def finches_index(request):
  return render(request, 'finches/index.html', { 'finches': finches })