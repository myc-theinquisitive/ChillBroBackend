# Generated by Django 3.2.4 on 2021-11-23 17:07

import Address.helpers1
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Address', '0004_cities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cities',
            name='icon_url',
        ),
        migrations.AddField(
            model_name='cities',
            name='image_url',
            field=models.ImageField(default='', max_length=300, storage=django.core.files.storage.FileSystemStorage('django.core.files.storage.FileSystemStorage'), upload_to=Address.helpers1.upload_image_to_city_icon),
            preserve_default=False,
        ),
    ]
