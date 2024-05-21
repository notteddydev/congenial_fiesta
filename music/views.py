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

        if tune.download():
            return HttpResponseRedirect(reverse("tune-list"))
        
        return HttpResponseNotFound("YouTube video not found.")