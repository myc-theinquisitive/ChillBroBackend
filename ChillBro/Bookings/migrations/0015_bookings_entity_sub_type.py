# Generated by Django 3.2.4 on 2022-03-10 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0014_auto_20220309_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookings',
            name='entity_sub_type',
            field=models.CharField(blank=True, choices=[('HOTEL', 'HOTEL'), ('RESORT', 'RESORT'), ('GUESTHOUSE', 'GUESTHOUSE'), ('DORMITORY_MEN', 'DORMITORY_MEN'), ('DORMITORY_WOMEN', 'DORMITORY_WOMEN'), ('DORMITORY_ALL', 'DORMITORY_ALL'), ('PG_MEN', 'PG_MEN'), ('PG_WOMEN', 'PG_WOMEN'), ('PG_ALL', 'PG_ALL')], max_length=30, null=True),
        ),
    ]
