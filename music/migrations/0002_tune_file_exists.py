# Generated by Django 5.0.6 on 2024-05-20 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tune',
            name='file_exists',
            field=models.BooleanField(default=False),
        ),
    ]
