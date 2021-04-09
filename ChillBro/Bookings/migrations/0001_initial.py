# Generated by Django 2.2.8 on 2021-04-08 20:06

import Bookings.models
import Bookings.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('user', models.CharField(default=Bookings.validators.get_user_id, max_length=16, verbose_name='User Id')),
                ('coupon', models.CharField(max_length=16, validators=[Bookings.validators.check_coupon_id], verbose_name='Coupon Id')),
                ('booking_id', models.CharField(default=Bookings.models.get_order_id, max_length=50, primary_key=True, serialize=False, verbose_name='Order Id')),
                ('booking_date', models.DateTimeField()),
                ('total_money', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('entity_type', models.IntegerField(choices=[(1, 'Hotels'), (2, 'Transport'), (3, 'Rentals'), (4, 'Resorts'), (5, 'Events')], default=1)),
                ('order_status', models.IntegerField(choices=[(1, 'Ordered'), (2, 'Delivered'), (3, 'Cancelled')], default=1)),
                ('payment_status', models.IntegerField(choices=[(1, 'Not done'), (2, 'Done')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='RentBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_id', models.CharField(max_length=16, verbose_name='Booking Id')),
                ('product_id', models.CharField(max_length=16, verbose_name='Product Id')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_cancelled', models.BooleanField(default=False)),
            ],
            options={
                'unique_together': {('booking_id', 'product_id')},
            },
        ),
        migrations.CreateModel(
            name='OrderedProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=16, validators=[Bookings.validators.check_product_id], verbose_name='Product Id')),
                ('entity', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('quantity', models.IntegerField()),
                ('product_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('booking_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Orders', verbose_name='Order Id')),
            ],
            options={
                'unique_together': {('booking_id', 'product_id')},
            },
        ),
    ]
