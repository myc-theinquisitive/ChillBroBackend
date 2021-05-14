# Generated by Django 2.2.8 on 2021-05-09 17:43

import Bookings.helpers
import Bookings.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookings',
            fields=[
                ('id', models.CharField(default=Bookings.models.get_id, max_length=36, primary_key=True, serialize=False, verbose_name='Booking Id')),
                ('coupon', models.CharField(blank=True, max_length=36, null=True, verbose_name='Coupon Id')),
                ('booking_date', models.DateTimeField(default=datetime.datetime.now)),
                ('total_money', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('entity_type', models.CharField(choices=[('HOTEL', 'HOTEL'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL'), ('RESORT', 'RESORT'), ('EVENT', 'EVENT')], default='HOTEL', max_length=30)),
                ('booking_status', models.CharField(choices=[('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('CANCELLED', 'CANCELLED'), ('DONE', 'DONE')], default='PENDING', max_length=30)),
                ('payment_status', models.CharField(choices=[('PENDING', 'PENDING'), ('FAILED', 'FAILED'), ('DONE', 'DONE'), ('NOT_REQUIRED', 'NOT_REQUIRED')], default='PENDING', max_length=30)),
                ('payment_mode', models.CharField(choices=[('COD', 'COD'), ('ONLINE', 'ONLINE')], default='ONLINE', max_length=30)),
                ('entity_id', models.CharField(max_length=36)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
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
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Bookings')),
            ],
        ),
        migrations.CreateModel(
            name='CheckOutDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_out', models.DateTimeField(default=datetime.datetime.now)),
                ('caution_deposit_deductions', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('reason_for_deduction', models.CharField(default='', max_length=10000)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Bookings')),
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
            name='CheckOutImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Bookings.helpers.image_upload_to_check_out)),
                ('check_out', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.CheckOutDetails')),
            ],
        ),
        migrations.CreateModel(
            name='CheckInImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=Bookings.helpers.image_upload_to_check_in)),
                ('check_in', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.CheckInDetails')),
            ],
        ),
        migrations.CreateModel(
            name='CancelledDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancelled_time', models.DateTimeField(default=datetime.datetime.now)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Bookings')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessClientReportOnCustomer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reasons_selected', models.CharField(max_length=100)),
                ('additional_info', models.CharField(max_length=10000)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Bookings')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessClientProductCancellation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=36)),
                ('reason', models.CharField(max_length=1000)),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Bookings')),
                ('cancelled_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookedProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=36, verbose_name='Product Id')),
                ('quantity', models.IntegerField()),
                ('product_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('net_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('booking_status', models.CharField(choices=[('BOOKED', 'BOOKED'), ('CANCELLED', 'CANCELLED')], default='BOOKED', max_length=30)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bookings.Bookings', verbose_name='Booking')),
            ],
            options={
                'unique_together': {('booking', 'product_id')},
            },
        ),
    ]
