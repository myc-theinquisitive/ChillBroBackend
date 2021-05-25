# Generated by Django 2.2.8 on 2021-05-21 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0006_auto_20210520_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price_type',
            field=models.CharField(choices=[('PER_DAY', 'PER_DAY'), ('PER_HOUR', 'PER_HOUR'), ('PER_MONTH', 'PER_MONTH')], default='PER_DAY', max_length=30, verbose_name='Price Type'),
        ),
    ]
