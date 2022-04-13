from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BookDate

class BookDateForm(forms.ModelForm):
    title = forms.CharField(max_length=100)
    month = forms.IntegerField()
    year = forms.IntegerField()
    class Meta:
        model = BookDate
        fields = ('notes',)

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',)
