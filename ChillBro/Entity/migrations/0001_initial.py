# Generated by Django 2.2.8 on 2021-05-09 17:43

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
            name='EntityUPI',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('upi_id', models.CharField(max_length=321, validators=[django.core.validators.MinLengthValidator(5), Entity.validations.validate_upi_id])),
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
                ('type', models.CharField(choices=[('HOTEL', 'HOTEL'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL')], max_length=30)),
                ('status', models.CharField(choices=[('ONLINE', 'ONLINE'), ('OFFLINE', 'OFFLINE')], default='ONLINE', max_length=30)),
                ('address_id', models.CharField(max_length=36)),
                ('pan_no', models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Entity.validations.validate_pan])),
                ('registration_no', models.CharField(max_length=21, validators=[django.core.validators.MinLengthValidator(21), Entity.validations.validate_registration])),
                ('gst_in', models.CharField(max_length=15, validators=[django.core.validators.MinLengthValidator(15), Entity.validations.validate_gst])),
                ('aadhar_no', models.CharField(max_length=14, validators=[django.core.validators.MinLengthValidator(14), Entity.validations.validate_aadhar])),
                ('pan_image', models.ImageField(upload_to=Entity.helpers.upload_pan_image_for_entity)),
                ('registration_image', models.ImageField(upload_to=Entity.helpers.upload_registration_image_for_entity)),
                ('gst_image', models.ImageField(upload_to=Entity.helpers.upload_gst_image_for_entity)),
                ('aadhar_image', models.ImageField(upload_to=Entity.helpers.upload_aadhar_image_for_entity)),
                ('is_verified', models.BooleanField(default=False)),
                ('active_from', models.DateTimeField(blank=True, null=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.EntityAccount')),
                ('upi', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.EntityUPI')),
            ],
        ),
        migrations.CreateModel(
            name='EntityVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verified_status', models.CharField(choices=[('VERIFIED', 'VERIFIED'), ('REJECTED', 'REJECTED'), ('YET_TO_VERIFY', 'YET_TO_VERIFY')], default='YET_TO_VERIFY', max_length=30)),
                ('comments', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Entity.MyEntity', verbose_name='Entity')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
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
