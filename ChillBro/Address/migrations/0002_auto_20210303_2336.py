# Generated by Django 2.2.8 on 2021-03-03 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Address', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address_line',
            field=models.CharField(max_length=250, verbose_name='Address Line'),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(choices=[('VSKP', 'VISAKHAPATNAM')], default='VISAKHAPATNAM', max_length=30, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.CharField(choices=[('IND', 'INDIA')], default='INDIA', max_length=30, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='address',
            name='extend_address',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Extend Address'),
        ),
        migrations.AlterField(
            model_name='address',
            name='landmark',
            field=models.CharField(max_length=250, verbose_name='Landmark'),
        ),
        migrations.AlterField(
            model_name='address',
            name='latitude',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='address',
            name='longitude',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Longitude'),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone_number',
            field=models.CharField(max_length=10, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='address',
            name='pincode',
            field=models.CharField(max_length=10, verbose_name='Pincode'),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(choices=[('AP', 'ANDHRA PRADESH')], default='ANDHRA PRADESH', max_length=30, verbose_name='State'),
        ),
    ]
