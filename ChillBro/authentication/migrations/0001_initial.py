# Generated by Django 2.2.8 on 2021-06-29 17:46

import authentication.models
import authentication.validations
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(10), authentication.validations.validate_phone], verbose_name='phone_number')),
                ('otp', models.TextField(default=authentication.models.random_string, max_length=6)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('expiry_time', models.DateTimeField(default=authentication.models.getExpiryTime)),
            ],
        ),
        migrations.CreateModel(
            name='SignupCode',
            fields=[
                ('code', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ipaddr', models.GenericIPAddressField(verbose_name='ip address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PasswordResetCode',
            fields=[
                ('code', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailChangeCode',
            fields=[
                ('code', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('email', models.EmailField(max_length=255, verbose_name='email address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
