# Generated by Django 2.2.8 on 2021-06-15 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WishList', '0007_auto_20210613_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='entity_type',
            field=models.CharField(blank=True, choices=[('STAY', 'STAY'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL'), ('EVENT', 'EVENT')], max_length=30, null=True),
        ),
    ]
