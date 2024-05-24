# Generated by Django 5.0.6 on 2024-05-24 10:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0006_alter_album_options_alter_genre_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tune',
            name='album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.album'),
        ),
        migrations.AlterField(
            model_name='tune',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='music.genre'),
        ),
    ]
