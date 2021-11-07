# Generated by Django 3.2.4 on 2021-11-06 06:26

import Product.BaseProduct.helpers
import Product.Category.helpers
import Product.Dormitory.helpers
import Product.Hotel.helpers
import Product.PG.helpers
import Product.Places.helpers
import Product.Resort.helpers
import Product.TravelAgency.helpers
import Product.TravelPackages.helpers
import Product.VehicleTypes.helpers
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0010_auto_20211030_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amenities',
            name='icon_url',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.Hotel.helpers.image_upload_to_amenities),
        ),
        migrations.AlterField(
            model_name='categoryimage',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.Category.helpers.upload_image_to_category),
        ),
        migrations.AlterField(
            model_name='dormitoryamenities',
            name='icon_url',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.Dormitory.helpers.image_upload_to_dormitory_amenities),
        ),
        migrations.AlterField(
            model_name='pgamenities',
            name='icon_url',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.PG.helpers.image_upload_to_pg_amenities),
        ),
        migrations.AlterField(
            model_name='placeimage',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.Places.helpers.upload_image_to_place),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.BaseProduct.helpers.image_upload_to_product),
        ),
        migrations.AlterField(
            model_name='resortamenities',
            name='icon_url',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.Resort.helpers.image_upload_to_resort_amenities),
        ),
        migrations.AlterField(
            model_name='travelagencyimage',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.TravelAgency.helpers.image_upload_to_travel_agency),
        ),
        migrations.AlterField(
            model_name='travelcharacteristics',
            name='icon_url',
            field=models.ImageField(max_length=300, storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.TravelAgency.helpers.upload_image_to_travel_characteristics),
        ),
        migrations.AlterField(
            model_name='travelpackageimage',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.TravelPackages.helpers.image_upload_to_travel_package),
        ),
        migrations.AlterField(
            model_name='vehiclecharacteristics',
            name='icon_url',
            field=models.ImageField(max_length=300, storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.VehicleTypes.helpers.upload_image_to_vehicle_characteristics),
        ),
        migrations.AlterField(
            model_name='vehicletype',
            name='image',
            field=models.ImageField(max_length=300, storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Product.VehicleTypes.helpers.upload_image_to_vehicle_type),
        ),
    ]
