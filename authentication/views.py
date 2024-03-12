from pyexpat.errors import messages

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from . forms import RegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import auth

def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account has been created!')
            login(request,user)
            return redirect('/home')
    else:
        form=RegistrationForm()

    context={'registerationForm': form}
    return render(request, 'authentication/signUp.html', context)

def login_user(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get('username')
            password = request.POST.get('password')
            user=authenticate(request, email=email, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('')

    context = {'loginForm': form}
    return render(request, 'authentication/login.html', context)

def logout(request):
    auth.logout(request)
    return redirect('')

def reset_password(request):
    template= 'authentication/resetPassword.html'
    message='We send verification code to your email. You can check your inbox.'
   #if request.method == 'POST':
