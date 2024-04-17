from django.contrib import admin
from .models import Card

class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_id', 'user', 'balance', 'card_number', 'token', 'type', 'system')

admin.site.register(Card, CardAdmin)
