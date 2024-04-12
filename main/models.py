from django.db import models
from authentication.models import CustomUser
import uuid

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cards')
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=16, unique=True)
    token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.card_number
