# Generated by Django 5.0.6 on 2024-06-14 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0017_tune_is_remix'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='album',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='album',
            name='reference',
            field=models.CharField(default='', max_length=150),
            preserve_default=False,
        ),
    ]