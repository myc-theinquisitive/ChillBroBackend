# Generated by Django 2.2.8 on 2021-04-29 21:41

import Product.BaseProduct.helpers
import Product.BaseProduct.models
import Product.Category.helpers
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField()),
                ('icon_url', models.ImageField(upload_to=Product.Category.helpers.iconUrlImage)),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Parent Category')),
            ],
        ),
        migrations.CreateModel(
            name='TimeStampModel',
            fields=[
                ('id', models.CharField(default=Product.BaseProduct.models.getId, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('timestampmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Product.TimeStampModel')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('Hotel', 'Hotel'), ('Transport', 'Transport'), ('Rental', 'Rental')], default='Rental', max_length=30, validators=[Product.BaseProduct.models.validate_product_type], verbose_name='Product Type')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discounted_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('featured', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('DELETED', 'DELETED')], default='PENDING', max_length=20)),
                ('quantity', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Category')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            bases=('Product.timestampmodel',),
        ),
        migrations.CreateModel(
            name='HotelRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='HotelAvailableAmenities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_available', models.BooleanField(default=False)),
                ('amenity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Amenities', verbose_name='Amenities')),
                ('hotel_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.HotelRoom', verbose_name='Hotel')),
            ],
            options={
                'unique_together': {('hotel_room', 'amenity')},
            },
        ),
        migrations.CreateModel(
            name='CategoryImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Product.Category.helpers.uploadImageToCategoryIcons)),
                ('order', models.IntegerField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category')),
            ],
            options={
                'unique_together': {('category', 'order')},
            },
        ),
        migrations.CreateModel(
            name='SellerProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_id', models.CharField(max_length=36)),
                ('selling_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product Seller')),
            ],
            options={
                'unique_together': {('product', 'seller_id')},
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Product.BaseProduct.helpers.image_upload_to_product)),
                ('order', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Product')),
            ],
            options={
                'unique_together': {('product', 'order')},
            },
        ),
    ]
