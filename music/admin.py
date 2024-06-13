import json
import os
import random

from datetime import datetime, timedelta

from django.contrib import admin
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest

from django_celery_beat.models import ClockedSchedule, PeriodicTask

from shutil import copy2

from .models import Album, Artist, Genre, Tag, Tune, TuneOrganiser

def create_tune_folders_for_many_to_many_queryset(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[TuneOrganiser]):
    for item in queryset:
        if not os.path.isdir(item.dir_path):
            os.mkdir(item.dir_path)

        filter = {self.model._meta.verbose_name_plural: item.id}

        tunes = Tune.objects.filter(**filter)

        for tune in tunes:
            tune_file_path = f"{item.dir_path}/{tune.file_name}"
            copy2(tune.full_file_path, tune_file_path)

def create_tune_folders_for_one_to_many_queryset(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[TuneOrganiser]):
    ids = queryset.values_list('id', flat=True)
    tunes = dict()
    filter = {f"{self.model._meta.verbose_name}_id__in": ids}
    for tune in Tune.objects.filter(**filter):
        tunes.setdefault(getattr(tune, f"{self.model._meta.verbose_name}_id"), []).append(tune)

    for item in queryset:
        if not os.path.isdir(item.dir_path):
            os.mkdir(item.dir_path)

        related_tunes = tunes[item.id]
        
        for related_tune in related_tunes:
            related_tune_file_path = f"{item.dir_path}/{related_tune.file_name}"
            copy2(related_tune.full_file_path, related_tune_file_path)

class AlbumAdmin(admin.ModelAdmin):
    actions = [create_tune_folders_for_one_to_many_queryset]

    def tracks(self: admin.ModelAdmin, obj: Album):
        if obj.is_single:
            return "Single"
        
        if obj.is_complete:
            return "Full Album"
        
        count = Tune.objects.filter(album__id=obj.id).count()

        if count > obj.track_count:
            return "ATTENTION"
        
        return f"{count}/{obj.track_count}"

    list_display = ("name", "artist", "tracks",)
    list_filter = ("artist",)

class ArtistAdmin(admin.ModelAdmin):
    actions = [create_tune_folders_for_many_to_many_queryset]

class GenreAdmin(admin.ModelAdmin):
    actions = [create_tune_folders_for_one_to_many_queryset]

class TagAdmin(admin.ModelAdmin):
    actions = [create_tune_folders_for_many_to_many_queryset]

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
            second_delay = (int(os.environ.get('DOWNLOAD_INTERVAL_SECONDS')) * counter) + random.randint(int(os.environ.get('DOWNLOAD_DEVIATION_LOWER')), int(os.environ.get('DOWNLOAD_DEVIATION_HIGHER')))
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
    list_display = ("name", "view_artists", "album", "view_downloaded",)
    list_filter = ("tags", "album__year", "artists", "album", "genre",)


admin.site.register(Album, AlbumAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Tune, TuneAdmin)
