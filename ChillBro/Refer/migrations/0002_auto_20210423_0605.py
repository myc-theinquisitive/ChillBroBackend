# Generated by Django 2.2.8 on 2021-04-23 06:05

import Refer.validations
import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Refer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referbusinessclient',
            name='id',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='referbusinessclient',
            name='primary_contact',
            field=models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Refer.validations.validate_phone]),
        ),
        migrations.AlterField(
            model_name='referbusinessclient',
            name='secondary_contact',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(10), Refer.validations.validate_phone]),
        ),
    ]
