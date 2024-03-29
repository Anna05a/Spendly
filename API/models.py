from django.db import models

class Card(models.Model):
    id = models.CharField(primary_key=True, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=16, unique=True)
    token = models.CharField(max_length=100, blank=True, null=True)

    def str(self):
        return self.card_number
