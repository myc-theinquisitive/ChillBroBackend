# Generated by Django 3.2.4 on 2021-07-04 10:19

import HelpCenter.helpers
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessClientFAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=100)),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('name', models.CharField(max_length=30)),
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='HelpCenterFAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=100)),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='HowToUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_type', models.CharField(max_length=30)),
                ('video_url', models.URLField(max_length=256)),
                ('title', models.CharField(max_length=30)),
                ('short_description', models.TextField()),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CarouselItem',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=30)),
                ('image', models.ImageField(max_length=300, storage=django.core.files.storage.FileSystemStorage('django.core.files.storage.FileSystemStorage'), upload_to=HelpCenter.helpers.upload_carousel_image)),
                ('redirection_url', models.URLField(max_length=256)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('DELETED', 'DELETED')], default='ACTIVE', max_length=20)),
                ('carousel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HelpCenter.carousel')),
            ],
        ),
    ]
