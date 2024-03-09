from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from  django.contrib.auth.models import User
from django.forms import CharField, EmailField


class RegistrationForm(UserCreationForm):
    email = EmailField(widget=forms.EmailInput())
    password1 = CharField(widget=forms.PasswordInput())
    password2 = CharField(widget=forms.PasswordInput())


class LoginForm(AuthenticationForm):
    email = EmailField(widget=forms.EmailInput())
    password = CharField(widget=forms.PasswordInput())

