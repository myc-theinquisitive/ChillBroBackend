# Generated by Django 2.2.8 on 2021-03-07 15:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coupons', '0002_auto_20210307_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allowedusersrule',
            name='users',
            field=models.ManyToManyField(blank=True, to='Coupons.AllowedIds', verbose_name='Users'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.now, editable=False, verbose_name='Created'),
        ),
    ]
