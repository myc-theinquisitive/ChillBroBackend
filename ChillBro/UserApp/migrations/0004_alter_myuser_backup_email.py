<<<<<<< HEAD
# Generated by Django 3.2.4 on 2021-08-07 08:24
=======
# Generated by Django 3.2.4 on 2021-08-02 10:37
>>>>>>> b7e5725af114eca60090c2cc982df2e4e67e1ec3

import ChillBro.validations
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0003_auto_20210801_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='backup_email',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, validators=[ChillBro.validations.validate_email], verbose_name='backup_email'),
        ),
    ]
