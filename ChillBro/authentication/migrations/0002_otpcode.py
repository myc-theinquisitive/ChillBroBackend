# Generated by Django 2.2.8 on 2021-02-28 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.TextField(max_length=10)),
                ('otp', models.TextField(max_length=6)),
                ('time', models.TimeField(auto_now_add=True)),
            ],
        ),
    ]
