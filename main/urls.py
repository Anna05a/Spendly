
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('statistics', views.statistics, name='statistics'),
    path('statistics_page', views.statistics_page, name='statistics_page'), # cтатистика після того як з карти підтягнулися категорії
    path('home_page', views.home_page, name='home_page'), #головна сторінка після того як додали карти
    path('add_card/', views.add_card, name='add_card'),
]
