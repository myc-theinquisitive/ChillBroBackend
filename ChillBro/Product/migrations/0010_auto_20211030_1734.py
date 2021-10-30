# Generated by Django 3.2.4 on 2021-10-30 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0009_auto_20211030_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travelagency',
            name='starting_point',
            field=models.CharField(choices=[('VISAKHAPATNAM', 'VISAKHAPATNAM'), ('SRIKAKULAM', 'SRIKAKULAM'), ('VIJAYANAGARAM', 'VIJAYANAGARAM'), ('EAST GODAVARI', 'EAST GODAVARI'), ('WEST GODAVARI', 'WEST GODAVARI')], max_length=36),
        ),
        migrations.AlterField(
            model_name='travelpackage',
            name='starting_point',
            field=models.CharField(choices=[('VISAKHAPATNAM', 'VISAKHAPATNAM'), ('SRIKAKULAM', 'SRIKAKULAM'), ('VIJAYANAGARAM', 'VIJAYANAGARAM'), ('EAST GODAVARI', 'EAST GODAVARI'), ('WEST GODAVARI', 'WEST GODAVARI')], max_length=36),
        ),
    ]
