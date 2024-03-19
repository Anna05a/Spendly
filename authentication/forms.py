import self
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from  django.contrib.auth.models import User
from django.forms import CharField, EmailField, TextInput
from django.utils.translation import gettext_lazy as _

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
            model = User
            fields = ('username','email','password1', 'password2')


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

class ResetPassword(PasswordResetForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['new_password1'].widget.attrs.attrs['placeholder']= 'Password'
            self.fields['new_password2'].widget.attrs.update['placeholder']='Password Confirmation'
        class Meta:
            model = get_user_model()
            fields = ("new_password1", "new_password2")
