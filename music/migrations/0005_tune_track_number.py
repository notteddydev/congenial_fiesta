# Generated by Django 5.0.6 on 2024-05-24 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_genre_album_tune_album_tune_genre'),
    ]

    operations = [
        migrations.AddField(
            model_name='tune',
            name='track_number',
            field=models.SmallIntegerField(default=1),
        ),
    ]