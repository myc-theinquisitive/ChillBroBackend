# Generated by Django 2.2.8 on 2021-04-30 13:23

import WishList.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WishList', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='id',
            field=models.CharField(default=WishList.models.getId, max_length=36, primary_key=True, serialize=False),
        ),
    ]
