
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.views import View

import username
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from validate_email import validate_email

from finances import settings
from .tokens import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from . forms import RegistrationForm, LoginForm, ResetPassword
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.models import auth, User


def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.is_active = False
            user.save()

            activate_email(request, user, form.cleaned_data.get('email'))
            return render(request,'authentication/verification.html',{'email':request.POST.get('email')})

    else:
        form = RegistrationForm()
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
    return redirect('login')

def reset_password(request):

   return render(request, 'authentication')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.add_message(request, messages.SUCCESS,
                             'Email verified, you can now login')
        return redirect(reverse('login'))

    return render(request, 'authentication/activation_failed.html', {"user": user})


def activate_email(request, user, to_email):
    subject = 'Activate your accounts'
    message=render_to_string('authentication/account_activation.html',{
        'user': user.username,
        'domain':get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'})

    email = EmailMessage(subject, message,to=[to_email])
    if email.send():
        messages.success(request, f'Please, check your email <b>{to_email}</b> and click on link below to activate your accounts.')
    else:
        messages.error(request, f'There is a problem with sending an email. Please, check if you typed it correctly')