# Generated by Django 2.2.8 on 2021-04-26 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReviewsRatings', '0002_auto_20210426_0009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewsratings',
            name='related_id',
            field=models.CharField(max_length=36, verbose_name='Related Id'),
        ),
    ]
