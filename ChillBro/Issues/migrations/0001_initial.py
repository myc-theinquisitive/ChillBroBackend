# Generated by Django 2.2.8 on 2021-04-13 19:03

import Issues.helpers
import Issues.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=100)),
                ('current_department', models.CharField(choices=[('CUSTOMER_CARE', 'CUSTOMER_CARE'), ('FINANCE', 'FINANCE')], default='CUSTOMER_CARE', max_length=100)),
                ('current_employeeId', models.CharField(blank=True, max_length=100, null=True)),
                ('issue_title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('entity', models.CharField(max_length=30)),
                ('order_id', models.CharField(max_length=30, validators=[Issues.validators.checkOrderId])),
                ('product_id', models.CharField(max_length=30, validators=[Issues.validators.checkProductId])),
                ('status', models.CharField(choices=[('TODO', 'TODO'), ('IN_PROGRESS', 'IN_PROGRESS'), ('DONE', 'DONE')], default='TODO', max_length=20)),
                ('final_resolution', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('employee_id', models.CharField(max_length=30)),
                ('employee_comment', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('transferred_to', models.CharField(choices=[('CUSTOMER_CARE', 'CUSTOMER_CARE'), ('FINANCE', 'FINANCE')], max_length=100)),
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('issue_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Issues.Issue')),
            ],
        ),
        migrations.CreateModel(
            name='IssueImage',
            fields=[
                ('image', models.ImageField(upload_to=Issues.helpers.image_upload_to_issue)),
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('issue_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Issues.Issue')),
            ],
        ),
    ]
