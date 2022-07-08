from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Feeding, User

class FeedingForm(ModelForm):
  class Meta:
    model = Feeding
    fields = ['date', 'meal']

class SignUpForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['email', 'username', 'first_name', 'last_name']
  