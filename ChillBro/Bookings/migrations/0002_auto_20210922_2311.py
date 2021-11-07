# Generated by Django 3.2.4 on 2021-09-22 17:41

import Bookings.helpers
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkindetails',
            name='id_image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Bookings.helpers.image_upload_to_user_id_proof),
        ),
        migrations.AlterField(
            model_name='checkinimages',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Bookings.helpers.image_upload_to_check_in),
        ),
        migrations.AlterField(
            model_name='checkoutimages',
            name='image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Bookings.helpers.image_upload_to_check_out),
        ),
    ]
