# Generated by Django 2.2.8 on 2021-05-25 19:20

import Product.BaseProduct.helpers
import Product.BaseProduct.models
import Product.Category.helpers
import Product.Category.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ('id', models.CharField(default=Product.Category.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField()),
                ('icon_url', models.ImageField(max_length=300, upload_to=Product.Category.helpers.update_image_to_category_icon)),
                ('parent_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Parent Category')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.CharField(default=Product.BaseProduct.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('HOTEL', 'HOTEL'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL')], default='RENTAL', max_length=30, verbose_name='Product Type')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discounted_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('price_type', models.CharField(choices=[('DAY', 'DAY'), ('HOUR', 'HOUR'), ('MONTH', 'MONTH')], default='DAY', max_length=30, verbose_name='Price Type')),
                ('featured', models.BooleanField(default=False)),
                ('has_sizes', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('is_combo', models.BooleanField(default=False)),
                ('active_from', models.DateTimeField(blank=True, null=True)),
                ('activation_status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('YET_TO_VERIFY', 'YET_TO_VERIFY'), ('REJECTED', 'REJECTED'), ('DELETED', 'DELETED')], default='YET_TO_VERIFY', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Category')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='RentalProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Entity')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HotelRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryPrices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('max_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('min_discount', models.IntegerField(default=0)),
                ('max_discount', models.IntegerField(default=0)),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Category')),
            ],
        ),
        migrations.CreateModel(
            name='SellerProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_id', models.CharField(max_length=36)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product Seller')),
            ],
            options={
                'unique_together': {('product', 'seller_id')},
            },
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=10, verbose_name='Size')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantity')),
                ('order', models.PositiveIntegerField(verbose_name='Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
            options={
                'ordering': ('order',),
                'unique_together': {('product', 'order'), ('product', 'size')},
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
                'ordering': ['order'],
                'unique_together': {('product', 'order')},
            },
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
            name='ComboProductItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('combo_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='combo_item', to='Product.Product', verbose_name='Combo Item')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
            options={
                'ordering': ['id'],
                'unique_together': {('product', 'combo_item')},
            },
        ),
        migrations.CreateModel(
            name='CategoryImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Product.Category.helpers.upload_image_to_category)),
                ('order', models.IntegerField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category')),
            ],
            options={
                'unique_together': {('category', 'order')},
            },
        ),
    ]
