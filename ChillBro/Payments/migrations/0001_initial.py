# Generated by Django 3.2.4 on 2021-07-04 10:20

import Payments.helpers
import Payments.models
from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RefundTransaction',
            fields=[
                ('id', models.CharField(default=Payments.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('booking_id', models.CharField(max_length=36)),
                ('entity_id', models.CharField(max_length=36)),
                ('entity_type', models.CharField(choices=[('STAY', 'STAY'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL'), ('EVENT', 'EVENT')], max_length=30)),
                ('booking_date', models.DateTimeField()),
                ('booking_start', models.DateTimeField()),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('bank_details', models.TextField(blank=True, null=True)),
                ('refund_reason', models.TextField()),
                ('payment_status', models.CharField(choices=[('PENDING', 'PENDING'), ('DONE', 'DONE'), ('CANCELLED', 'CANCELLED')], default='PENDING', max_length=30)),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('utr', models.CharField(blank=True, max_length=50, null=True)),
                ('mode', models.CharField(choices=[('NOT_DONE', 'NOT_DONE'), ('UPI', 'UPI'), ('COD', 'COD'), ('CARD', 'CARD')], default='NOT_DONE', max_length=10)),
                ('transaction_date', models.DateTimeField(blank=True, null=True)),
                ('initiated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookingTransaction',
            fields=[
                ('id', models.CharField(default=Payments.models.get_id, max_length=36, primary_key=True, serialize=False)),
                ('booking_id', models.CharField(max_length=36)),
                ('entity_id', models.CharField(max_length=36)),
                ('entity_type', models.CharField(choices=[('STAY', 'STAY'), ('TRANSPORT', 'TRANSPORT'), ('RENTAL', 'RENTAL'), ('EVENT', 'EVENT')], max_length=30)),
                ('total_money', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('booking_date', models.DateTimeField()),
                ('booking_start', models.DateTimeField()),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('utr', models.CharField(blank=True, max_length=50, null=True)),
                ('mode', models.CharField(choices=[('NOT_DONE', 'NOT_DONE'), ('UPI', 'UPI'), ('COD', 'COD'), ('CARD', 'CARD')], default='NOT_DONE', max_length=10)),
                ('transaction_date', models.DateTimeField(blank=True, null=True)),
                ('payment_status', models.CharField(choices=[('PENDING', 'PENDING'), ('DONE', 'DONE'), ('CANCELLED', 'CANCELLED')], default='PENDING', max_length=30)),
                ('paid_to', models.CharField(choices=[('ENTITY', 'ENTITY'), ('MYC', 'MYC'), ('CUSTOMER', 'CUSTOMER')], default='ENTITY', max_length=30)),
                ('paid_by', models.CharField(choices=[('ENTITY', 'ENTITY'), ('MYC', 'MYC'), ('CUSTOMER', 'CUSTOMER')], default='MYC', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('transaction_proof', models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage('django.core.files.storage.FileSystemStorage'), upload_to=Payments.helpers.image_upload_to_transaction_proof)),
                ('credited_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
