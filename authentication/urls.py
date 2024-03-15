from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('sign-up', views.sign_up, name='sign-up'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('reset_password', auth_views.PasswordResetView.as_view(template_name="authentication/forgot_password.html"), name='forgot_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="authentication/reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/reset_password.html"), name='password_reset'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="authentication/verification.html"), name='password_reset_complete')

]
