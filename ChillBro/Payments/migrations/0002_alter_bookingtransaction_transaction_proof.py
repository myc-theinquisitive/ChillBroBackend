# Generated by Django 3.2.4 on 2021-08-28 08:57

import Payments.helpers
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingtransaction',
            name='transaction_proof',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage('/home/ffs2imp1oh0k/public_html/chillbro_backend/'), upload_to=Payments.helpers.image_upload_to_transaction_proof),
        ),
    ]
