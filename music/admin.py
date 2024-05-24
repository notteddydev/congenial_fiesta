import json
import os
import random

from datetime import datetime, timedelta

from django.contrib import admin
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest

from django_celery_beat.models import ClockedSchedule, PeriodicTask

from .models import Album, Artist, Genre, Tag, Tune


class TuneAdmin(admin.ModelAdmin):
    @admin.action(description="Set metadata for selected tunes")
    def set_queryset_metadata(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Tune]):
        for tune in queryset:
            if tune.downloaded:
                tune.set_metadata()

    @admin.action(description="Download selected tunes")
    def download_queryset(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Tune]):
        counter = 0
        now = datetime.now()
        task = "music.tasks.tune_download"

        existing_periodic_download_tasks = PeriodicTask.objects.filter(task=task)

        if existing_periodic_download_tasks.exists():
            existing_periodic_download_tasks.delete()

        for tune in queryset:
            if tune.downloaded:
                continue

            periodic_task_name = f"Downloading tune with id: {tune.id}"
            second_delay = (os.environ.get('DOWNLOAD_INTERVAL_SECONDS') * counter) + random.randint(os.environ.get('DOWNLOAD_DEVIATION_LOWER'), os.environ.get('DOWNLOAD_DEVIATION_HIGHER'))
            clocked_time = now + timedelta(seconds=second_delay)
            schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)
            transaction.on_commit(lambda: PeriodicTask.objects.create(
                args=json.dumps([tune.id]),
                clocked=schedule,
                name=periodic_task_name,
                one_off=True,
                task=task
            ))
            counter += 1

    @admin.action(description="Trim selected tunes")
    def trim_queryset(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Tune]):
        for tune in queryset:
            if tune.downloaded:
                tune.trim()

    def delete_queryset(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Tune]) -> None:
        for tune in queryset:
            tune.remove_file()

        return super().delete_queryset(request, queryset)

    def view_artists(self: admin.ModelAdmin, obj: Tune):
        return ", ".join([artist.name for artist in obj.artists.all()])

    def view_downloaded(self: admin.ModelAdmin, obj: Tune):
        if obj.downloaded:
            return "Downloaded"

        return "-"

    actions = [download_queryset, set_queryset_metadata, trim_queryset]
    list_display = ("name", "view_artists", "view_downloaded",)


admin.site.register(Album)
admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Tag)
admin.site.register(Tune, TuneAdmin)
