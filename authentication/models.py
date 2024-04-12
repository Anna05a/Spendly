from django.contrib.auth.models import AbstractUser
from django.db import models
from main.models import Card


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    cards = models.ManyToManyField(Card, blank=True)
    groups = models.ManyToManyField('auth.Group', )
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')

    def __str__(self):
        return self.username
