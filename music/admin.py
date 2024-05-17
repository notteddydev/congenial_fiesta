from django.contrib import admin

from .models import Artist, Participation, Tag, Tune


admin.site.register(Artist)
admin.site.register(Participation)
admin.site.register(Tag)
admin.site.register(Tune)
