# Generated by Django 2.2.8 on 2021-04-27 20:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0004_merge_20210427_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='payment_status',
        ),
        migrations.AlterField(
            model_name='bookings',
            name='booking_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
