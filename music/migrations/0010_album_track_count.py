# Generated by Django 5.0.6 on 2024-06-11 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0009_alter_album_options_alter_album_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='track_count',
            field=models.SmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
