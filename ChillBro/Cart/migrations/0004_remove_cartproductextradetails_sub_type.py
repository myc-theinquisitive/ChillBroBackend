# Generated by Django 2.2.8 on 2021-06-18 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0003_auto_20210619_0050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartproductextradetails',
            name='sub_type',
        ),
    ]
