# Generated by Django 2.2.8 on 2021-06-22 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0007_auto_20210622_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='transportbookingdetails',
            name='km_limit_choosen',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
