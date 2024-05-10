from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=16, unique=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    system = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.card_number

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    card_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, unique=True)
    payment_desc = models.CharField(max_length=30, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.card_id.card_number} - {self.time} - {self.amount} {self.currency} - {self.category}"