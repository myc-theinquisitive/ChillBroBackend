# Generated by Django 2.2.8 on 2021-02-28 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20210228_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpcode',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
