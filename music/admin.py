from django.contrib import admin

from .models import Artist, Tag, Tune


admin.site.register(Artist)
admin.site.register(Tag)
admin.site.register(Tune)
