from django.contrib import admin

from .models import Artist, Tag, Tune


class TuneAdmin(admin.ModelAdmin):

    def view_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()])
    
    list_display = ("name", "view_artists",)


admin.site.register(Artist)
admin.site.register(Tag)
admin.site.register(Tune, TuneAdmin)
