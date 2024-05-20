from django.urls import path

from . import views

urlpatterns = [
    path("tunes", views.TuneListView.as_view())
]