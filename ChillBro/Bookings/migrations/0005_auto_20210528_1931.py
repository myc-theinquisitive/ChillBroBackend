# Generated by Django 2.2.8 on 2021-05-28 19:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0004_bookedproducts_is_combo'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bookedproducts',
            unique_together={('booking', 'product_id', 'is_combo')},
        ),
    ]
