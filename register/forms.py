from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField( required=True)
    first_Name = forms.CharField(max_length=50, required=True)
    last_Name = forms.CharField(max_length=50, required=True)
    Phone_Number = forms.CharField( max_length=13, required=False)

    #profile_pic = forms.ImageField( required=False)


    class Meta:
        model = User
        fields = ["username","first_Name","last_Name","email","Phone_Number","password1","password2"]