# Generated by Django 3.2.4 on 2021-12-04 07:41

import django.core.files.storage
from django.db import migrations, models
import Address.helpers


class Migration(migrations.Migration):

    dependencies = [
        ('Address', '0005_auto_20211123_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cities',
            name='image_url',
            field=models.ImageField(max_length=300, storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Address.helpers.upload_image_to_city_icon),
        ),
    ]
