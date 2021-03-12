# Generated by Django 2.2.8 on 2021-03-09 00:20

import Coupons.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coupons', '0004_auto_20210308_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(default=Coupons.helpers.get_random_code, max_length=15, unique=True, verbose_name='Coupon Code'),
        ),
    ]
