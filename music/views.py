import os

from django.shortcuts import render
from django.views.generic import ListView, View
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from pydub import AudioSegment
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

from .models import Tune


class TuneListView(ListView):
    model = Tune


class TuneListenView(View):
    def post(self, request, id):
        tune = Tune.objects.get(pk=id)

        try:
            yt = YouTube(tune.youtube_link)
        except VideoUnavailable:
            return HttpResponseNotFound("YouTube video not found.")

        video = yt.streams.filter(progressive=True).first()
        mp3 = video.download(filename=tune.file_name, output_path=os.environ.get('TUNES_DIR'))

        if mp3 is None:
            return HttpResponseNotFound("YouTube video not found.")
        
        song = AudioSegment.from_file(mp3)
        song.export(tune.full_file_path, format="mp3")

        return HttpResponseRedirect(reverse("tune-list"))