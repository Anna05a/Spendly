# Generated by Django 5.0.3 on 2024-04-16 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_alter_customuser_email'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]