import os

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Artist, Tag, Tune


class TuneAdmin(admin.ModelAdmin):
    @admin.action(description="Set the title and artist metadata")
    def set_queryset_metadata(self, request: HttpRequest, queryset: QuerySet[Tune]):
        for tune in queryset:
            if tune.downloaded:
                tune.set_metadata()


    @admin.action(description="Download")
    def download_queryset(self, request: HttpRequest, queryset: QuerySet[Tune]):
        for tune in queryset:
            if not tune.downloaded:
                tune.set_file_name()
                if tune.download():
                    tune.save()


    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Tune]) -> None:
        for tune in queryset:
            tune.remove_file()

        return super().delete_queryset(request, queryset)

    def view_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()])
    
    actions = [download_queryset, set_queryset_metadata]
    list_display = ("name", "view_artists",)


admin.site.register(Artist)
admin.site.register(Tag)
admin.site.register(Tune, TuneAdmin)
