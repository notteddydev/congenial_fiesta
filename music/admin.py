import os

from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Artist, Tag, Tune


class TuneAdmin(admin.ModelAdmin):
    @admin.action(description="Set the title and artist metadata")
    def set_metadata(self, request: HttpRequest, queryset: QuerySet[Any]):
        for tune in queryset:
            tune.set_metadata()


    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        for tune in queryset:
            tune.remove_file()

        return super().delete_queryset(request, queryset)

    def view_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()])
    
    actions = [set_metadata]
    list_display = ("name", "view_artists",)


admin.site.register(Artist)
admin.site.register(Tag)
admin.site.register(Tune, TuneAdmin)
