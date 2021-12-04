# Generated by Django 3.2.4 on 2021-11-27 09:26

import Payments.helpers
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0004_alter_bookingtransaction_transaction_proof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingtransaction',
            name='transaction_proof',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage('django.core.files.storage.FileSystemStorage'), upload_to=Payments.helpers.image_upload_to_transaction_proof),
        ),
    ]
