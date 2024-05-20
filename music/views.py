import pygame

from django.shortcuts import render
from django.views.generic import ListView, View
from django.conf import settings
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
        mp3 = video.download(filename=tune.file_name, output_path=settings.TUNES_DIR)

        if mp3 is None:
            return HttpResponseNotFound("YouTube video not found.")
        
        song = AudioSegment.from_file(mp3)
        song.export(tune.full_file_path, format="mp3")

        tune.file_exists = True
        tune.save()

        return HttpResponseRedirect(reverse("tune-list"))


class TunePlayView(View):
    def get(self, request, id):
        tune = Tune.objects.get(pk=id)

        print(tune.full_file_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tune.full_file_path)
        pygame.mixer.music.play()

        return HttpResponseRedirect(reverse("tune-list"))
