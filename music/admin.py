import datetime
import json

from django.contrib import admin
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest

from django_celery_beat.models import ClockedSchedule, PeriodicTask

from .models import Artist, Tag, Tune
from .tasks import tune_download


class TuneAdmin(admin.ModelAdmin):
    @admin.action(description="Set metadata for selected tunes")
    def set_queryset_metadata(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Tune]):
        for tune in queryset:
            if tune.downloaded:
                tune.set_metadata()

    @admin.action(description="Download selected tunes")
    def download_queryset(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Tune]):
        # Set a 20 min delay between each download.
        minute_delay = 20
        counter = 0
        for tune in queryset:
            if tune.downloaded:
                continue

            now = datetime.datetime.now()
            clocked_time = now + datetime.timedelta(minutes=minute_delay*counter)
            schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)

            counter += 1

            task_name = f"Downloading tune with id: {tune.id}"

            PeriodicTask.objects.get(name=task_name).delete()
            transaction.on_commit(lambda: PeriodicTask.objects.create(
                clocked=schedule,
                name=f"Downloading tune with id: {tune.id}",
                one_off=True,
                task="music.tasks.tune_download",
                args=json.dumps([tune.id])
            ))
            

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

    actions = [download_queryset, set_queryset_metadata]
    list_display = ("name", "view_artists", "view_downloaded",)


admin.site.register(Artist)
admin.site.register(Tag)
admin.site.register(Tune, TuneAdmin)
