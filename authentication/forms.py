from django import forms
from  django.contrib.auth.models import User
class RegistrationForm():
    email=forms.EmailField(label='email')
    password=forms.CharField(widget=forms.PasswordInput)

    class Meta():
        model = User
        fields = ["email", "password"]