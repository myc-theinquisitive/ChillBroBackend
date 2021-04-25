# Generated by Django 2.2.8 on 2021-04-24 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Entity', '0002_auto_20210424_0557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myentity',
            name='city',
        ),
        migrations.RemoveField(
            model_name='myentity',
            name='pincode',
        ),
        migrations.AddField(
            model_name='myentity',
            name='address_id',
            field=models.CharField(default='1', max_length=36),
            preserve_default=False,
        ),
    ]
