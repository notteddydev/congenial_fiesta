# Generated by Django 5.0.6 on 2024-05-27 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0008_alter_tune_album_alter_tune_genre'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='album',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='album',
            unique_together={('name', 'year', 'artist')},
        ),
    ]