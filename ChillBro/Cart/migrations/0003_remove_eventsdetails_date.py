# Generated by Django 3.2.4 on 2021-10-10 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0002_eventsdetails_eventsprices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventsdetails',
            name='date',
        ),
    ]
