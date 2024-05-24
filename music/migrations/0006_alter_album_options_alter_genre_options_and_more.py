# Generated by Django 5.0.6 on 2024-05-24 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_tune_track_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='album',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['name']},
        ),
        migrations.AlterUniqueTogether(
            name='tune',
            unique_together={('album', 'track_number')},
        ),
    ]
