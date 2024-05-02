
from django.urls import path
from . import views
#from .views import StatisticsPageView


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('statistics', views.StatisticsView.as_view(), name='statistics'),
    path('statistics_page', views.StatisticsPageView.as_view(), name='statistics_page'),
    path('home_page', views.HomePageView.as_view(), name='home_page'),
    path('add_card/', views.AddCardView.as_view(), name='add_card'),
    path('get_payments/<str:card_id>/', views.GetPaymentsView.as_view(), name='get_payments'),
    path('delete_card/<str:card_id>/', views.DeleteCardView.as_view(), name='delete_card'),
    path('refresh', views.RefreshCardView.as_view(), name='refresh_card_data'),
    path('clear_history', views.ClearCardsView.as_view(), name='clear_history')
]
