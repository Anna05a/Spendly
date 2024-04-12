from django.contrib import admin
from .models import Card

class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance', 'card_number', 'token')  

admin.site.register(Card, CardAdmin)
