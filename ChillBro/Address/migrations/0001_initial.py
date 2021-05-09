# Generated by Django 2.2.8 on 2021-05-09 16:42

import Address.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.CharField(default=Address.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Name')),
                ('phone_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Phone Number')),
                ('pincode', models.CharField(blank=True, max_length=10, null=True, verbose_name='Pincode')),
                ('address_line', models.CharField(blank=True, max_length=250, null=True, verbose_name='Address Line')),
                ('extend_address', models.CharField(blank=True, max_length=250, null=True, verbose_name='Extend Address')),
                ('landmark', models.CharField(blank=True, max_length=250, null=True, verbose_name='Landmark')),
                ('city', models.CharField(choices=[('VSKP', 'VISAKHAPATNAM')], default='VISAKHAPATNAM', max_length=30, verbose_name='City')),
                ('state', models.CharField(choices=[('AP', 'ANDHRA PRADESH')], default='ANDHRA PRADESH', max_length=30, verbose_name='State')),
                ('country', models.CharField(choices=[('IND', 'INDIA')], default='INDIA', max_length=30, verbose_name='Country')),
                ('latitude', models.CharField(blank=True, max_length=15, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(blank=True, max_length=15, null=True, verbose_name='Longitude')),
            ],
        ),
    ]
