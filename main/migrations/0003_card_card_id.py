# Generated by Django 5.0.4 on 2024-04-12 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_card_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='card_id',
            field=models.CharField(default='misha', max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
