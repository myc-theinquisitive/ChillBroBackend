# Generated by Django 2.2.8 on 2021-06-30 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0006_auto_20210630_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookedproducts',
            name='excess_net_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
        migrations.AddField(
            model_name='bookedproducts',
            name='excess_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
        migrations.AddField(
            model_name='bookings',
            name='excess_total_net_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
        migrations.AddField(
            model_name='bookings',
            name='excess_total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
