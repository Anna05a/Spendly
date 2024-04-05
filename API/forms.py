import self
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from  django.contrib.auth.models import User
from django.forms import CharField, EmailField, TextInput
from django.utils.translation import gettext_lazy as _

class TokenForm(forms.Form):
    token=forms.CharField()