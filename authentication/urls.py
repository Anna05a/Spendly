from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import SignUpView, LoginView,LogoutView,DeleteUserView

urlpatterns = [
    path('', SignUpView.as_view(), name='sign-up'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_form.html',email_template_name='authentication/password_reset_email.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
    path('delete_profile/', DeleteUserView.as_view(), name='delete_profile'),

]
