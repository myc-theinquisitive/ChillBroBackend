# Generated by Django 2.2.8 on 2021-05-08 13:42

import Product.Category.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0006_categoryprices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.CharField(default=Product.Category.models.get_id, max_length=36, primary_key=True, serialize=False),
        ),
    ]
