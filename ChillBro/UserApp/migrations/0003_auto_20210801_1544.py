# Generated by Django 3.2.4 on 2021-08-01 10:14

import UserApp.validations
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0002_myuser_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='backup_email',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='backup_email'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='backup_phone_number',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(10), UserApp.validations.validate_phone], verbose_name='backup_phone_number'),
        ),
    ]
