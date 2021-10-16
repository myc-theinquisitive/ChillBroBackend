# Generated by Django 3.2.4 on 2021-10-15 06:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0004_rename_product_businessclientquotation_vehicle'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventsDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('phone_no', models.IntegerField(max_length=10)),
                ('alternate_no', models.IntegerField(max_length=10)),
                ('email', models.CharField(max_length=50)),
                ('booked_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookedproducts')),
            ],
        ),
        migrations.CreateModel(
            name='EventsPrices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('quantity', models.IntegerField(default=0)),
                ('event_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.eventsdetails')),
            ],
        ),
    ]
