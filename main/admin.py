from django.contrib import admin
from .models import Card, Category

class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_id', 'user', 'balance', 'card_number', 'token', 'type', 'system')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_id', 'user', 'time', 'amount', 'currency', 'category')

admin.site.register(Card, CardAdmin)
admin.site.register(Category, CategoryAdmin)
