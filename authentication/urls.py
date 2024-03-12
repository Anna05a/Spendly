from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('sign-up', views.sign_up, name='sign-up'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout, name='logout'),
    path('reset_password', auth_views.PasswordResetView.as_view(template_name="authentication/reset_password.html"), name='reset_password'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')

]
