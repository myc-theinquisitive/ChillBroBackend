# Generated by Django 2.2.8 on 2021-04-26 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReviewsRatings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewsratings',
            name='related_id',
            field=models.CharField(max_length=32, verbose_name='Related Id'),
        ),
    ]
