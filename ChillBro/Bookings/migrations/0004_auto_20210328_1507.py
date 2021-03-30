# Generated by Django 2.2.8 on 2021-03-28 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0003_auto_20210328_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproducts',
            name='quantity',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_status',
            field=models.IntegerField(choices=[(1, 'Ordered'), (2, 'Delivered'), (3, 'Cancelled')], default=1),
        ),
        migrations.AlterField(
            model_name='orders',
            name='payment_status',
            field=models.IntegerField(choices=[(1, 'Not done'), (2, 'Done')], default=1),
        ),
    ]
