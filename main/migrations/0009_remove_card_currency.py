# Generated by Django 5.0.3 on 2024-05-16 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_card_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='currency',
        ),
    ]
