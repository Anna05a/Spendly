from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_up, name='sign-up')
]
