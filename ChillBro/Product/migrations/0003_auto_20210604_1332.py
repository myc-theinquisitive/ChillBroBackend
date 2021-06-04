# Generated by Django 2.2.8 on 2021-06-04 13:32

import Product.Vehicle.validations
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0002_vehiclecharacteristics_display_front'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.CharField(choices=[('HOTEL', 'HOTEL'), ('RENTAL', 'RENTAL'), ('HIRE_A_VEHICLE', 'HIRE_A_VEHICLE')], default='RENTAL', max_length=30, verbose_name='Product Type'),
        ),
        migrations.CreateModel(
            name='HireAVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_no', models.CharField(max_length=15, validators=[django.core.validators.MinLengthValidator(8), Product.Vehicle.validations.validate_vehicle_registration_no])),
                ('default_driver', models.CharField(max_length=36)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
                ('vehicle_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.VehicleType', verbose_name='VehicleType')),
            ],
        ),
    ]
