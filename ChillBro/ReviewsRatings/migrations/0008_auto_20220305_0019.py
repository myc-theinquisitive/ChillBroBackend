# Generated by Django 3.2.4 on 2022-03-04 18:49

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ReviewsRatings', '0007_alter_reviewimage_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='BCAppFeedbackAndSuggestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opinion', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('category', models.CharField(choices=[('SUGGESTION', 'SUGGESTION'), ('SOMETHING IS NOT QUITE RIGHT', 'SOMETHING IS NOT QUITE RIGHT'), ('COMPLIMENT', 'COMPLIMENT')], default='SUGGESTION', max_length=30)),
                ('comment', models.TextField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Reviewed By')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerAppFeedbackAndSuggestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
                ('module', models.CharField(max_length=100)),
                ('comment', models.TextField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Reviewed By')),
            ],
        ),
        migrations.DeleteModel(
            name='FeedbackAndSuggestions',
        ),
    ]
