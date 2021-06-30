# Generated by Django 2.2.8 on 2021-06-29 17:47

import Entity.helpers
import Entity.validations
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('icon_url', models.ImageField(upload_to=Entity.helpers.image_upload_to_amenities)),
            ],
        ),
        migrations.CreateModel(
            name='EntityAccount',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('bank_name', models.CharField(max_length=60)),
                ('account_no', models.CharField(max_length=18, validators=[django.core.validators.MinLengthValidator(9), Entity.validations.validate_bank_account_no])),
                ('ifsc_code', models.CharField(max_length=11, validators=[django.core.validators.MinLengthValidator(11), Entity.validations.validate_ifsc_code])),
                ('account_type', models.CharField(choices=[('SAVINGS', 'SAVINGS'), ('CURRENT', 'CURRENT'), ('SALARY', 'SALARY'), ('FIXED_DEPOSIT', 'FIXED_DEPOSIT')], max_length=20)),
                ('account_holder_name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='EntityRegistration',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('pan_no', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Entity.validations.validate_pan])),
                ('registration_no', models.CharField(max_length=21, validators=[django.core.validators.MinLengthValidator(21), Entity.validations.validate_registration])),
                ('gst_in', models.CharField(max_length=15, validators=[django.core.validators.MinLengthValidator(15), Entity.validations.validate_gst])),
                ('aadhar_no', models.CharField(max_length=14, validators=[django.core.validators.MinLengthValidator(14), Entity.validations.validate_aadhar])),
                ('pan_image', models.ImageField(max_length=500, upload_to=Entity.helpers.upload_pan_image_for_entity)),
                ('registration_image', models.ImageField(max_length=500, upload_to=Entity.helpers.upload_registration_image_for_entity)),
                ('gst_image', models.ImageField(max_length=500, upload_to=Entity.helpers.upload_gst_image_for_entity)),
                ('aadhar_image', models.ImageField(max_length=500, upload_to=Entity.helpers.upload_aadhar_image_for_entity)),
            ],
        ),
        migrations.CreateModel(
            name='EntityUPI',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('upi_id', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(5), Entity.validations.validate_upi_id])),
                ('phone_pe', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Entity.validations.validate_phone])),
                ('g_pay', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Entity.validations.validate_phone])),
                ('pay_tm', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Entity.validations.validate_phone])),
            ],
        ),
        migrations.CreateModel(
            name='MyEntity',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('STAY', 'STAY'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL'), ('EVENT', 'EVENT')], max_length=30)),
                ('sub_type', models.CharField(blank=True, choices=[('HOTEL', 'HOTEL'), ('RESORT', 'RESORT'), ('GUESTHOUSE', 'GUESTHOUSE'), ('DORMITORY_MEN', 'DORMITORY_MEN'), ('DORMITORY_WOMEN', 'DORMITORY_WOMEN'), ('DORMITORY_ALL', 'DORMITORY_ALL'), ('PG_MEN', 'PG_MEN'), ('PG_WOMEN', 'PG_WOMEN'), ('PG_ALL', 'PG_ALL')], max_length=30, null=True)),
                ('status', models.CharField(choices=[('ONLINE', 'ONLINE'), ('OFFLINE', 'OFFLINE')], default='OFFLINE', max_length=30)),
                ('address_id', models.CharField(max_length=36)),
                ('active_from', models.DateTimeField(blank=True, null=True)),
                ('activation_status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('REJECTED', 'REJECTED'), ('YET_TO_VERIFY', 'YET_TO_VERIFY'), ('DELETED', 'DELETED')], default='YET_TO_VERIFY', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.EntityAccount')),
                ('registration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.EntityRegistration')),
                ('upi', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.EntityUPI')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EntityVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.MyEntity', verbose_name='Entity')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EntityImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Entity.helpers.upload_image_for_entity)),
                ('order', models.IntegerField()),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Entity.MyEntity')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('entity', 'order')},
            },
        ),
        migrations.CreateModel(
            name='EntityAvailableAmenities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_available', models.BooleanField(default=False)),
                ('amenity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Entity.Amenities', verbose_name='Amenities')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Entity.MyEntity', verbose_name='Entity')),
            ],
            options={
                'unique_together': {('entity', 'amenity')},
            },
        ),
        migrations.CreateModel(
            name='BusinessClientEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Entity.MyEntity', verbose_name='Booking')),
            ],
            options={
                'unique_together': {('entity', 'business_client')},
            },
        ),
    ]
