# Generated by Django 2.2.8 on 2021-03-07 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind_of_stream', models.IntegerField(choices=[(1, 'Business Client'), (2, 'Individual')], default=1, max_length=100)),
                ('travels_name', models.CharField(max_length=100)),
                ('contact_person_name', models.CharField(max_length=100)),
                ('contact_no', models.CharField(max_length=10)),
                ('alternate_no', models.CharField(max_length=10)),
                ('office_no', models.CharField(max_length=10)),
                ('website_url', models.CharField(max_length=100)),
                ('address_1', models.TextField(max_length=1000)),
                ('address_2', models.TextField(max_length=1000)),
                ('pin_code', models.CharField(max_length=6)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('type_of_address', models.IntegerField(choices=[(1, 'Home'), (2, 'Office'), (3, 'Others')], default=1, max_length=100)),
                ('send_to', models.IntegerField(choices=[(1, 'All'), (2, 'individual')], max_length=100)),
                ('employee_name', models.CharField(max_length=100)),
            ],
        ),
    ]
