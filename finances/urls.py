from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', include('main.urls')),
    path('', include('authentication.urls')),
    path('accounts/', include('allauth.urls')),
]
