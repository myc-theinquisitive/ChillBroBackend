# Generated by Django 3.2.4 on 2021-09-22 17:41

import HelpCenter.helpers
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HelpCenter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselitem',
            name='image',
            field=models.ImageField(max_length=300, storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=HelpCenter.helpers.upload_carousel_image),
        ),
    ]
