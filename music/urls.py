from django.urls import path

from . import views

urlpatterns = [
    path("tunes", views.TuneListView.as_view(), name="tune-list"),
    path("tunes/<int:id>/listen", views.TuneListenView.as_view(), name="tune-listen")
]