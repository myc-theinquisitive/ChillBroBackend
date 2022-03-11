# Generated by Django 3.2.4 on 2022-03-11 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0015_bookings_entity_sub_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookings',
            name='booking_status',
            field=models.CharField(choices=[('YET_TO_APPROVE', 'YET_TO_APPROVE'), ('BUSINESS_CLIENT_REJECTED', 'BUSINESS_CLIENT_REJECTED'), ('BUSINESS_CLIENT_NOT_ACTED', 'BUSINESS_CLIENT_NOT_ACTED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('CANCELLED', 'CANCELLED'), ('COMPLETED', 'COMPLETED')], default='YET_TO_APPROVE', max_length=30),
        ),
    ]
