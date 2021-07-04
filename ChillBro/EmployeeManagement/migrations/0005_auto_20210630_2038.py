# Generated by Django 3.2.4 on 2021-06-30 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmployeeManagement', '0004_auto_20210628_1944'),
    ]

    operations = [
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee', models.CharField(max_length=36, unique=True, verbose_name='Employee ID')),
                ('year_salary', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='leaves',
            name='approved_by',
            field=models.CharField(default=1, max_length=36, verbose_name='Manager'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaves',
            name='leave_type',
            field=models.CharField(choices=[('SICK', 'SICK'), ('PERSONAL', 'PERSONAL'), ('CASUAL', 'CASUAL'), ('PAID', 'PAID')], default=1, max_length=36),
            preserve_default=False,
        ),
    ]
