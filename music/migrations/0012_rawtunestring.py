# Generated by Django 5.0.6 on 2024-06-13 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0011_alter_album_track_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawTuneString',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=255)),
            ],
        ),
    ]
