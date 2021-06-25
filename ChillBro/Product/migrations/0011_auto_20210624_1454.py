# Generated by Django 2.2.8 on 2021-06-24 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0010_auto_20210624_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hireavehicledistanceprice',
            name='hire_a_vehicle',
        ),
        migrations.RemoveField(
            model_name='hireavehicledurationdetails',
            name='hire_a_vehicle',
        ),
        migrations.AddField(
            model_name='hireavehicle',
            name='distance_price',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Product.HireAVehicleDistancePrice'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hireavehicle',
            name='duration_details',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Product.HireAVehicleDurationDetails'),
            preserve_default=False,
        ),
    ]
