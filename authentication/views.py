from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import login
def sign_up(request):
    if request.method == 'POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form=RegistrationForm()
    return render(request, 'authentication/signUp.html',{'form': form})

