from django.contrib import messages
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, logout
from django.contrib import auth
from django.contrib.auth.models import User
from django.views import View

from main.models import Card
from .forms import RegistrationForm, LoginForm
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError


class SignUpView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'authentication/signUp.html', {'registerForm': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return render(request, 'authentication/verification.html', {'email': request.POST.get('email')})
        return render(request, 'authentication/signUp.html', {'registerForm': form})




def activate_email(request, user, to_email):
    subject = 'Activate your accounts'
    message = render_to_string('authentication/account_activation.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(subject, message, to=[to_email])
    if email.send():
        messages.success(request,
                         f'Please, check your email {to_email} and click on link below to activate your accounts.')
    else:
        messages.error(request,
                       f'There is a problem with sending an email. Please, check if you typed it correctly')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, DjangoUnicodeDecodeError):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.SUCCESS, 'Email verified, you can now login')
        return redirect(reverse('home'))
    else:
        return render(request, 'authentication/activation_failed.html', {"user": user})



class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'authentication/login.html', {'loginForm': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                if Card.objects.filter(user=request.user).exists():
                    return redirect('home_page')
                else:
                    return redirect('home')
        return render(request, 'authentication/login.html', {'loginForm': form})



class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')



class DeleteUserView(View):
    def get(self, request):
        user = request.user
        user.delete()
        return redirect('sign-up')



class ResetPasswordView(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')