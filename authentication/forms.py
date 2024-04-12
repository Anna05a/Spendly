from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import CustomUser

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label=_(""),
        max_length=30,
        help_text=None,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        help_text=None,
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password confirmation'}),
        help_text=None,
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_(""),
        max_length=30,
        help_text=None,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        help_text=None,
    )
    fields = [ 'username', 'password' ]

