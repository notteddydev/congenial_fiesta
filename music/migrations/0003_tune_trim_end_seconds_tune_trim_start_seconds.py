# Generated by Django 5.0.6 on 2024-05-23 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_tune_attempt_download_on_create'),
    ]

    operations = [
        migrations.AddField(
            model_name='tune',
            name='trim_end_seconds',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tune',
            name='trim_start_seconds',
            field=models.IntegerField(default=0),
        ),
    ]
