from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from . forms import RegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import auth

def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('')
    else:
        form=RegistrationForm()

    context={'registerationForm': form}
    return render(request, 'authentication/signUp.html', context)

def login(request):
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
    return redirect('home')
