from django.shortcuts import render
from django.views.generic import ListView

from .models import Tune

class TuneListView(ListView):
    model = Tune