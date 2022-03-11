from ..models import generate_refer_and_earn_code
from django.db import migrations


def update_refer_and_earn_fields(apps, schema_editor):
    MyModel = apps.get_model('UserApp', 'MyUser')
    for row in MyModel.objects.all():
        row.refer_code = generate_refer_and_earn_code()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0013_myuser_refer_code'),
    ]

    operations = [
        migrations.RunPython(update_refer_and_earn_fields),
    ]
