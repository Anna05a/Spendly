from django.contrib import messages
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, logout
from django.contrib import auth
from .models import CustomUser
from .forms import RegistrationForm, LoginForm
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.contrib.auth import get_user_model

User = get_user_model()


def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return render(request, 'authentication/verification.html', {'email': request.POST.get('email')})
    else:
        form = RegistrationForm()
    return render(request, 'authentication/signUp.html', {'registerForm': form})



def login_user(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = CustomUser.objects.get(username=username)
            if user.check_password(password):
                auth.login(request, user)
                return redirect('home_page')
    return render(request, 'authentication/login.html', {'loginForm': form})



def logout(request):
    auth.logout(request)
    return redirect('login')


def delete_user(request):
    user = request.user
    user.delete()
    return redirect('sign-up')



def reset_password(request):
    return render(request, 'authentication/reset_password.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, DjangoUnicodeDecodeError):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.SUCCESS, 'Email verified, you can now login')
        return redirect(reverse('home'))
    else:
        return render(request, 'authentication/activation_failed.html', {"user": user})


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
        messages.success(request, f'Please, check your email {to_email} and click on link below to activate your accounts.')
    else:
        messages.error(request, f'There is a problem with sending an email. Please, check if you typed it correctly')
