from django.contrib import messages


import username
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token

from . forms import RegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import auth, User


def sign_up(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('home')

    context = {'registerForm': form}
    return render(request, 'authentication/signUp.html', context)
def login_user(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user=authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('home')

    context = {'loginForm': form}
    return render(request, 'authentication/login.html', context)

def logout(request):
    auth.logout(request)
    return redirect('home')

def reset_password(request):

   return render(request, 'authentication')

def activate(request, uidb64, token):
    return redirect('home')

def activate_email(request, user, to_email):
    subject = 'Activate your accaunt'
    message=render_to_string('authentication/account_activation.html',
                             {'user': user.username,
                                    'domain':get_current_site(request).domain,
                              'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                              'token': account_activation_token.make_token(user),
                              'protocol': 'https' if request.is_secure() else 'http'})
    email = EmailMessage(subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Please, check your email <b>{to_email}</b> and click on link below to activate your account.')
    else:
        messages.error(request, f'There is a problem with sending an email. Please, check if you typed it correctly')