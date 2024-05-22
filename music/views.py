import os

from django.shortcuts import render
from django.views.generic import ListView, View
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from pytube.exceptions import VideoUnavailable

from .models import Tune
from .tasks import tune_download


class TuneListView(ListView):
    model = Tune


class TuneListenView(View):
    def post(self, request, id):
        tune = Tune.objects.get(pk=id)
        tune.set_file_name()
        
        if tune.download():
            tune.save()
            return HttpResponseRedirect(reverse("tune-list"))
        
        return HttpResponseNotFound("YouTube video not found.")