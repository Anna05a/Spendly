
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('statistics', views.statistics, name='statistics')
]
