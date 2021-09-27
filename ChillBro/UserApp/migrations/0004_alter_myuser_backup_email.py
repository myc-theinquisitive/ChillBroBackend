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
