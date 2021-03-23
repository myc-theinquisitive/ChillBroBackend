# Generated by Django 2.2.8 on 2021-03-24 01:00

import authentication.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.TextField(max_length=10, unique=True)),
                ('otp', models.TextField(default=authentication.models.random_string, max_length=6)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
