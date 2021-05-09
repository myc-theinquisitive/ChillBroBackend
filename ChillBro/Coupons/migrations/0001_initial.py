# Generated by Django 2.2.8 on 2021-05-09 16:42

import Coupons.helpers
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedEntitiesRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entities', models.TextField(blank=True, null=True, verbose_name='Entities')),
                ('all_entities', models.BooleanField(default=True, verbose_name='All entities?')),
            ],
            options={
                'verbose_name': 'Allowed Entities Rule',
                'verbose_name_plural': 'Allowed Entities Rules',
            },
        ),
        migrations.CreateModel(
            name='AllowedProductsRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('products', models.TextField(blank=True, null=True, verbose_name='Products')),
                ('all_products', models.BooleanField(default=True, verbose_name='All Products?')),
            ],
            options={
                'verbose_name': 'Allowed Product Rule',
                'verbose_name_plural': 'Allowed Product Rules',
            },
        ),
        migrations.CreateModel(
            name='AllowedUsersRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('users', models.TextField(blank=True, null=True, verbose_name='Users')),
                ('all_users', models.BooleanField(default=True, verbose_name='All users?')),
            ],
            options={
                'verbose_name': 'Allowed User Rule',
                'verbose_name_plural': 'Allowed User Rules',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=Coupons.helpers.get_random_code, max_length=15, unique=True, verbose_name='Coupon Code')),
                ('title', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(null=True)),
                ('terms_and_conditions', models.TextField(null=True)),
                ('times_used', models.IntegerField(default=0, editable=False, verbose_name='Times used')),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False, verbose_name='Created')),
            ],
        ),
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.TextField(max_length=16, verbose_name='Order id')),
                ('discount_obtained', models.IntegerField(default=0, verbose_name='Discount Obtained')),
                ('used_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Used on')),
            ],
        ),
        migrations.CreateModel(
            name='CouponUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times_used', models.IntegerField(default=0, editable=False, verbose_name='Times used')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.Coupon', verbose_name='Coupon')),
            ],
            options={
                'verbose_name': 'Coupon User',
                'verbose_name_plural': 'Coupon Users',
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0, verbose_name='Value')),
                ('is_percentage', models.BooleanField(default=False, verbose_name='Is percentage?')),
                ('max_value_if_percentage', models.IntegerField(default=100, editable=models.BooleanField(default=False, verbose_name='Is percentage?'), verbose_name='Max Discount (if percentage)')),
            ],
            options={
                'verbose_name': 'Discount',
                'verbose_name_plural': 'Discounts',
            },
        ),
        migrations.CreateModel(
            name='MaxUsesRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_uses', models.BigIntegerField(default=0, verbose_name='Maximum uses')),
                ('is_infinite', models.BooleanField(default=False, verbose_name='Infinite uses?')),
                ('uses_per_user', models.IntegerField(default=1, verbose_name='Uses per User')),
            ],
            options={
                'verbose_name': 'Max Uses Rule',
                'verbose_name_plural': 'Max Uses Rules',
            },
        ),
        migrations.CreateModel(
            name='ValidityRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(null=True, verbose_name='Start date')),
                ('end_date', models.DateTimeField(null=True, verbose_name='End date')),
                ('is_active', models.BooleanField(default=False, verbose_name='Is active?')),
                ('minimum_order_value', models.IntegerField(default=0, verbose_name='Minimum Order value to avail the coupon')),
            ],
            options={
                'verbose_name': 'Validity Rule',
                'verbose_name_plural': 'Validity Rules',
            },
        ),
        migrations.CreateModel(
            name='Ruleset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowed_entities', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.AllowedEntitiesRule', verbose_name='Allowed entities rule')),
                ('allowed_products', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.AllowedProductsRule', verbose_name='Allowed products rule')),
                ('allowed_users', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.AllowedUsersRule', verbose_name='Allowed users rule')),
                ('max_uses', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.MaxUsesRule', verbose_name='Max uses rule')),
                ('validity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.ValidityRule', verbose_name='Validity rule')),
            ],
            options={
                'verbose_name': 'Ruleset',
                'verbose_name_plural': 'Rulesets',
            },
        ),
        migrations.CreateModel(
            name='CouponUserUsages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_usage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.CouponUsage', verbose_name='Coupon Usage')),
                ('coupon_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.CouponUser', verbose_name='Coupon User')),
            ],
        ),
        migrations.AddField(
            model_name='couponuser',
            name='coupon_usages',
            field=models.ManyToManyField(through='Coupons.CouponUserUsages', to='Coupons.CouponUsage'),
        ),
        migrations.AddField(
            model_name='couponuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='couponusage',
            name='coupon_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.CouponUser', verbose_name='Coupon User'),
        ),
        migrations.CreateModel(
            name='CouponHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=Coupons.helpers.get_random_code, max_length=15, verbose_name='Coupon Code')),
                ('title', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(null=True)),
                ('terms_and_conditions', models.TextField(null=True)),
                ('times_used', models.IntegerField(default=0, editable=False, verbose_name='Times used')),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False, verbose_name='Created')),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Changed By')),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.Discount')),
                ('ruleset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.Ruleset', verbose_name='Ruleset')),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.Discount'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='ruleset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Coupons.Ruleset', verbose_name='Ruleset'),
        ),
    ]
