# Generated by Django 5.0.6 on 2024-06-14 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0016_remove_rawtunestring_possible_duplicate'),
    ]

    operations = [
        migrations.AddField(
            model_name='tune',
            name='is_remix',
            field=models.BooleanField(default=False),
        ),
    ]
