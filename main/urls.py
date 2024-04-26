
from django.urls import path
from . import views
#from .views import StatisticsPageView


urlpatterns = [
    path('', views.home, name='home'),
    path('statistics', views.statistics, name='statistics'),
    path('statistics_page', views.statistics_page, name='statistics_page'), # cтатистика після того як з карти підтягнулися категорії
    path('home_page', views.home_page, name='home_page'), #головна сторінка після того як додали карти
    path('add_card/', views.add_card, name='add_card'),
    path('get_payments/<str:card_id>/', views.get_payments, name='get_payments'),
    path('delete_card/<str:card_id>/', views.delete_card, name='delete_card'),
    path('refresh', views.refresh_card, name='refresh_card_data'),
    path('clear_history', views.clear_cards, name='clear_history')
]
