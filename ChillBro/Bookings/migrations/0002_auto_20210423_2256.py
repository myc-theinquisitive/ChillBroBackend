# Generated by Django 2.2.8 on 2021-04-23 22:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookings',
            name='booking_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 23, 22, 56, 4, 489682)),
        ),
    ]
