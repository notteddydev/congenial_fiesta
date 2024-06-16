import re
import subprocess
import urllib.parse
import urllib.request

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import View

from .models import RawTuneString, Tune
    
class RawTuneStringInfoView(View):
    def get(self, request, id):
        brave_path = '/usr/bin/brave-browser'
        rts = get_object_or_404(RawTuneString, id=id)

        search_keyword = urllib.parse.quote(rts.info, safe='')
        yt_search_url = f"https://www.youtube.com/results?search_query={search_keyword}"
        html = urllib.request.urlopen(yt_search_url)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        distinct_video_ids = list(dict.fromkeys(video_ids))
        first_video_ids = distinct_video_ids[:4]

        genius_query = urllib.parse.quote(f"site:genius.com {rts.info}")
        google_query = urllib.parse.quote(rts.info)
        genre_query = urllib.parse.quote(f"genre {rts.info}")

        urls = [
            f"https://www.youtube.com/watch?v={first_video_ids[0]}",
            yt_search_url,
            f"https://www.google.com/search?q={genius_query}",
            f"https://www.google.com/search?q={google_query}",
            f"https://www.google.com/search?q={genre_query}"
        ]

        duplicates = Tune.objects.filter(youtube_id__in=first_video_ids).all()

        if len(duplicates):
            for dupe in duplicates:
                urls.append(request.build_absolute_uri(reverse("admin:music_tune_change", args=[dupe.id])))

        for url in urls:
            subprocess.run([brave_path, '--incognito', '--new-tab', url])

        # return HttpResponseRedirect(request.META["HTTP_REFERER"])
        return HttpResponseRedirect(reverse("admin:music_rawtunestring_delete", args=[rts.id]))