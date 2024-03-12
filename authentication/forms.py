from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from  django.contrib.auth.models import User
from django.forms import CharField, EmailField


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm):
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(AuthenticationForm):
    email = EmailField(widget=forms.EmailInput())
    password = CharField(widget=forms.PasswordInput())

