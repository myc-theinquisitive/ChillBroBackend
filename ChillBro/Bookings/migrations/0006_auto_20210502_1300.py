# Generated by Django 2.2.8 on 2021-05-02 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bookings', '0005_auto_20210427_2028'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookings',
            old_name='user',
            new_name='created_by',
        ),
    ]
