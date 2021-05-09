# Generated by Django 2.2.8 on 2021-05-09 16:43

import Refer.validations
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReferBusinessClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_type', models.CharField(max_length=100)),
                ('business_name', models.CharField(max_length=100)),
                ('owner_name', models.CharField(max_length=100)),
                ('primary_contact', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Refer.validations.validate_phone])),
                ('secondary_contact', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(10), Refer.validations.validate_phone])),
                ('address', models.TextField()),
            ],
        ),
    ]
