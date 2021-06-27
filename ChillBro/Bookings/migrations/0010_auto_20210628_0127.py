# Generated by Django 2.2.8 on 2021-06-27 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0009_auto_20210624_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransportBookingDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_type', models.CharField(blank=True, choices=[('ROUND', 'ROUND'), ('SINGLE', 'SINGLE')], max_length=30, null=True)),
                ('pickup_location', models.CharField(blank=True, max_length=36, null=True)),
                ('drop_location', models.CharField(blank=True, max_length=36, null=True)),
                ('starting_km_value', models.PositiveIntegerField(default=0)),
                ('ending_km_value', models.PositiveIntegerField(default=0)),
                ('km_limit_choosen', models.PositiveIntegerField(default=0)),
                ('booked_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.BookedProducts')),
            ],
        ),
        migrations.CreateModel(
            name='TransportBookingDistancePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('km_hour_limit', models.PositiveIntegerField(default=0)),
                ('km_day_limit', models.PositiveIntegerField(default=0)),
                ('excess_km_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('is_kms_infinity', models.BooleanField(default=False)),
                ('single_trip_return_value_per_km', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
        ),
        migrations.DeleteModel(
            name='TransportBookingDistanceDetails',
        ),
        migrations.AddField(
            model_name='transportbookingdetails',
            name='distance_price',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.TransportBookingDistancePrice'),
        ),
        migrations.AddField(
            model_name='transportbookingdetails',
            name='duration_details',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.TransportBookingDurationDetails'),
        ),
    ]
