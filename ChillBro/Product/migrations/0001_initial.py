# Generated by Django 2.2.8 on 2021-06-29 17:48

import Product.BaseProduct.helpers
import Product.BaseProduct.models
import Product.Category.helpers
import Product.Category.models
import Product.Hotel.helpers
import Product.Places.helpers
import Product.Places.models
import Product.TravelPackages.helpers
import Product.TravelPackages.models
import Product.TravelPackages.validations
import Product.Vehicle.validations
import Product.VehicleTypes.helpers
import Product.VehicleTypes.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('icon_url', models.ImageField(upload_to=Product.Hotel.helpers.image_upload_to_amenities)),
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
            name='CategoryProduct',
            fields=[
                ('id', models.CharField(default=Product.Category.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category')),
            ],
        ),
        migrations.CreateModel(
            name='HireAVehicleDistancePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('excess_km_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('km_hour_limit', models.PositiveIntegerField()),
                ('km_day_limit', models.PositiveIntegerField()),
                ('is_km_infinity', models.BooleanField(default=False)),
                ('single_trip_return_value_per_km', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='HireAVehicleDurationDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('day_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('excess_hour_duration_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('excess_day_duration_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('min_hour_duration', models.PositiveIntegerField(default=1)),
                ('max_hour_duration', models.PositiveIntegerField(default=24)),
                ('min_day_duration', models.PositiveIntegerField(default=1)),
                ('max_day_duration', models.PositiveIntegerField(default=31)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.CharField(default=Product.Places.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('address_id', models.CharField(max_length=36)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Category')),
            ],
            options={
                'unique_together': {('name', 'category')},
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.CharField(default=Product.BaseProduct.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('HOTEL', 'HOTEL'), ('RENTAL', 'RENTAL'), ('DRIVER', 'DRIVER'), ('VEHICLE', 'VEHICLE'), ('HIRE_A_VEHICLE', 'HIRE_A_VEHICLE'), ('TRAVEL_PACKAGE_VEHICLE', 'TRAVEL_PACKAGE_VEHICLE'), ('SELF_RENTAL', 'SELF_RENTAL')], default='RENTAL', max_length=30, verbose_name='Product Type')),
                ('seller_id', models.CharField(max_length=36)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discounted_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('price_type', models.CharField(choices=[('DAY', 'DAY'), ('HOUR', 'HOUR'), ('MONTH', 'MONTH')], default='DAY', max_length=30, verbose_name='Price Type')),
                ('featured', models.BooleanField(default=False)),
                ('has_sizes', models.BooleanField(default=False)),
                ('has_sub_products', models.BooleanField(default=False)),
                ('quantity_unlimited', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('is_combo', models.BooleanField(default=False)),
                ('active_from', models.DateTimeField(blank=True, null=True)),
                ('activation_status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('YET_TO_VERIFY', 'YET_TO_VERIFY'), ('REJECTED', 'REJECTED'), ('DELETED', 'DELETED')], default='YET_TO_VERIFY', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Category')),
                ('category_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.CategoryProduct', verbose_name='CategoryProduct')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='SelfRental',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('excess_price_per_hour', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='self_rental_product', to='Product.Product', verbose_name='Vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='TravelPackage',
            fields=[
                ('id', models.CharField(default=Product.TravelPackages.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('tags', models.TextField(validators=[Product.TravelPackages.validations.is_json])),
                ('duration_in_days', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Duration in days')),
                ('duration_in_nights', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Duration in nights')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Category')),
                ('category_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.CategoryProduct', verbose_name='Category Product')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleCharacteristics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('icon_url', models.ImageField(max_length=300, upload_to=Product.VehicleTypes.helpers.upload_image_to_vehicle_characteristics)),
                ('units', models.CharField(blank=True, max_length=30, null=True)),
                ('display_front', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.CharField(default=Product.VehicleTypes.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('no_of_people', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('wheel_type', models.CharField(choices=[('2 WHEELER', '2 WHEELER'), ('4 WHEELER', '4 WHEELER')], max_length=30)),
                ('image', models.ImageField(max_length=300, upload_to=Product.VehicleTypes.helpers.upload_image_to_vehicle_type)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Category', verbose_name='Category')),
                ('category_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.CategoryProduct', verbose_name='Category Product')),
            ],
            options={
                'unique_together': {('name', 'category', 'category_product')},
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_no', models.CharField(max_length=15, validators=[django.core.validators.MinLengthValidator(8), Product.Vehicle.validations.validate_vehicle_registration_no])),
                ('registration_type', models.CharField(choices=[('REGULAR', 'REGULAR'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL')], max_length=20)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle', to='Product.Product', verbose_name='Product')),
                ('vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.VehicleType', verbose_name='VehicleType')),
            ],
        ),
        migrations.CreateModel(
            name='TravelPackageVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
                ('travel_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='driver_for_vehicle', to='Product.TravelPackage', verbose_name='Default Driver')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travel_package_vehicle', to='Product.Product', verbose_name='Vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='SelfRentalDurationDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_hour_duration', models.PositiveIntegerField(default=1)),
                ('max_hour_duration', models.PositiveIntegerField(default=24)),
                ('min_day_duration', models.PositiveIntegerField(default=1)),
                ('max_day_duration', models.PositiveIntegerField(default=31)),
                ('self_rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.SelfRental')),
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
                ('max_no_of_people', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('product', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='HireAVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='driver_for_vehicle', to='Product.Product', verbose_name='Default Driver')),
                ('distance_price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.HireAVehicleDistancePrice')),
                ('duration_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.HireAVehicleDurationDetails')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_product', to='Product.Product', verbose_name='Vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_id', models.CharField(max_length=36)),
                ('licensed_from', models.PositiveIntegerField(help_text='Use the following format: <YYYY>', validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2021)])),
                ('preferred_vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='driver_preferred_vehicle', to='Product.VehicleType', verbose_name='Vehicle')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryProductPrices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('max_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('min_discount', models.IntegerField(default=0)),
                ('max_discount', models.IntegerField(default=0)),
                ('category_product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Product.CategoryProduct')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleTypeCharacteristics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50)),
                ('vehicle_characteristic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.VehicleCharacteristics', verbose_name='Vehicle Characteristic')),
                ('vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.VehicleType', verbose_name='Vehicle Type')),
            ],
            options={
                'unique_together': {('vehicle_type', 'vehicle_characteristic')},
            },
        ),
        migrations.CreateModel(
            name='TravelPackageImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Product.TravelPackages.helpers.image_upload_to_travel_package)),
                ('order', models.IntegerField()),
                ('travel_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.TravelPackage', verbose_name='Travel Package')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('travel_package', 'order')},
            },
        ),
        migrations.CreateModel(
            name='SelfRentalDistancePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('km_limit', models.PositiveIntegerField()),
                ('excess_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('is_infinity', models.BooleanField(default=False)),
                ('self_rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.SelfRental')),
            ],
            options={
                'unique_together': {('self_rental', 'km_limit')},
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
            name='PlaceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Product.Places.helpers.upload_image_to_place)),
                ('order', models.IntegerField()),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Place')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('place', 'order')},
            },
        ),
        migrations.CreateModel(
            name='PackagePlaces',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('in_return', models.BooleanField(default=False)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.Place', verbose_name='Package Place')),
                ('travel_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.TravelPackage', verbose_name='Travel Package')),
            ],
            options={
                'unique_together': {('travel_package', 'place', 'order')},
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
