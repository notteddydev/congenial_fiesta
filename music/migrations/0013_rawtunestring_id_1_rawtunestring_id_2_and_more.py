# Generated by Django 5.0.6 on 2024-06-13 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0012_rawtunestring'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawtunestring',
            name='id_1',
            field=models.CharField(blank=True, editable=False, max_length=11),
        ),
        migrations.AddField(
            model_name='rawtunestring',
            name='id_2',
            field=models.CharField(blank=True, editable=False, max_length=11),
        ),
        migrations.AddField(
            model_name='rawtunestring',
            name='id_3',
            field=models.CharField(blank=True, editable=False, max_length=11),
        ),
        migrations.AddField(
            model_name='rawtunestring',
            name='id_4',
            field=models.CharField(blank=True, editable=False, max_length=11),
        ),
        migrations.AddField(
            model_name='rawtunestring',
            name='id_5',
            field=models.CharField(blank=True, editable=False, max_length=11),
        ),
    ]
