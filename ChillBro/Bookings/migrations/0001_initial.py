# Generated by Django 3.2.4 on 2021-07-02 12:52

import Bookings.helpers
import Bookings.models
import datetime
from django.conf import settings
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
            name='BookedProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=36, verbose_name='Product Id')),
                ('quantity', models.IntegerField()),
                ('size', models.CharField(blank=True, max_length=10, null=True, verbose_name='Size')),
                ('is_combo', models.BooleanField(default=False)),
                ('has_sub_products', models.BooleanField(default=False)),
                ('hidden', models.BooleanField(default=False)),
                ('product_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('net_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('coupon_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('booking_status', models.CharField(choices=[('BOOKED', 'BOOKED'), ('CANCELLED', 'CANCELLED')], default='BOOKED', max_length=30)),
                ('excess_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('excess_net_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Bookings',
            fields=[
                ('id', models.CharField(default=Bookings.models.get_id, max_length=36, primary_key=True, serialize=False, verbose_name='Booking Id')),
                ('coupon', models.CharField(blank=True, max_length=36, null=True, verbose_name='Coupon Id')),
                ('booking_date', models.DateTimeField(default=datetime.datetime.now)),
                ('payment_mode', models.CharField(blank=True, choices=[('PARTIAL', 'PARTIAL'), ('FULL', 'FULL')], max_length=30, null=True)),
                ('total_money', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('total_net_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('total_coupon_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('entity_type', models.CharField(choices=[('STAY', 'STAY'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL'), ('EVENT', 'EVENT')], max_length=30)),
                ('booking_status', models.CharField(choices=[('YET_TO_APPROVE', 'YET_TO_APPROVE'), ('BUSINESS_CLIENT_REJECTED', 'BUSINESS_CLIENT_REJECTED'), ('BUSINESS_CLIENT_NOT_ACTED', 'BUSINESS_CLIENT_NOT_ACTED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('CANCELLED', 'CANCELLED'), ('DONE', 'DONE')], default='YET_TO_APPROVE', max_length=30)),
                ('payment_status', models.CharField(choices=[('PENDING', 'PENDING'), ('FAILED', 'FAILED'), ('DONE', 'DONE'), ('NOT_REQUIRED', 'NOT_REQUIRED')], default='PENDING', max_length=30)),
                ('entity_id', models.CharField(max_length=36)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('excess_total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('excess_total_net_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('otp', models.IntegerField(default=Bookings.models.generate_otp)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CheckInDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateTimeField(default=datetime.datetime.now)),
                ('is_caution_deposit_collected', models.BooleanField(default=False)),
                ('caution_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('id_proof_type', models.CharField(choices=[('AADHAR_CARD', 'AADHAR_CARD'), ('PAN_CARD', 'PAN_CARD'), ('VOTER_ID', 'VOTER_ID')], default='AADHAR_CARD', max_length=30)),
                ('id_image', models.ImageField(upload_to=Bookings.helpers.image_upload_to_user_id_proof)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings')),
            ],
        ),
        migrations.CreateModel(
            name='CheckOutDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_out', models.DateTimeField(default=datetime.datetime.now)),
                ('caution_deposit_deductions', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('reason_for_deduction', models.CharField(default='', max_length=10000)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings')),
            ],
        ),
        migrations.CreateModel(
            name='ReportCustomerReasons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TransportBookingDistanceDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('km_hour_limit', models.PositiveIntegerField(default=0)),
                ('km_day_limit', models.PositiveIntegerField(default=0)),
                ('excess_km_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('is_infinity', models.BooleanField(default=False)),
                ('single_trip_return_value_per_km', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('km_limit', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TransportBookingDurationDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('day_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('excess_hour_duration_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('excess_day_duration_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='TransportBookingDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_type', models.CharField(blank=True, choices=[('ROUND', 'ROUND'), ('SINGLE', 'SINGLE')], max_length=30, null=True)),
                ('pickup_location', models.CharField(blank=True, max_length=36, null=True)),
                ('drop_location', models.CharField(blank=True, max_length=36, null=True)),
                ('starting_km_value', models.PositiveIntegerField(default=0)),
                ('ending_km_value', models.PositiveIntegerField(default=0)),
                ('km_limit_choosen', models.PositiveIntegerField(default=0)),
                ('booked_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookedproducts')),
                ('distance_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.transportbookingdistancedetails')),
                ('duration_details', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Bookings.transportbookingdurationdetails')),
            ],
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('booking_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings')),
            ],
        ),
        migrations.CreateModel(
            name='CheckOutImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Bookings.helpers.image_upload_to_check_out)),
                ('check_out', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.checkoutdetails')),
            ],
        ),
        migrations.CreateModel(
            name='CheckInImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Bookings.helpers.image_upload_to_check_in)),
                ('check_in', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.checkindetails')),
            ],
        ),
        migrations.CreateModel(
            name='CancelledDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancelled_time', models.DateTimeField(default=datetime.datetime.now)),
                ('reason', models.TextField()),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessClientReportOnCustomer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reasons_selected', models.CharField(max_length=100)),
                ('additional_info', models.CharField(max_length=10000)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessClientProductCancellation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=36)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings')),
                ('cancelled_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='bookedproducts',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookings', verbose_name='Booking'),
        ),
        migrations.AddField(
            model_name='bookedproducts',
            name='parent_booked_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Bookings.bookedproducts', verbose_name='Parent Booked Product Id'),
        ),
        migrations.CreateModel(
            name='BusinessClientQuotation',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_by', models.CharField(max_length=36)),
                ('product', models.CharField(max_length=36)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('entity_id', models.CharField(max_length=36)),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.quotation')),
            ],
            options={
                'unique_together': {('created_by', 'quotation')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='bookedproducts',
            unique_together={('booking', 'product_id', 'hidden', 'parent_booked_product')},
        ),
    ]
