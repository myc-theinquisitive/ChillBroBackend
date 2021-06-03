# Generated by Django 2.2.8 on 2021-05-29 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0003_combocartproducts'),
    ]

    operations = [
        migrations.AddField(
            model_name='combocartproducts',
            name='quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='combocartproducts',
            name='size',
            field=models.CharField(default=1, max_length=10, verbose_name='Size'),
            preserve_default=False,
        ),
    ]
