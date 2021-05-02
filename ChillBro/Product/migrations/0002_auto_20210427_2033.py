# Generated by Django 2.2.8 on 2021-04-27 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('DELETED', 'DELETED')], default='PENDING', max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
