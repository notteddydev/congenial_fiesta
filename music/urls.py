from django.urls import path

from . import views

urlpatterns = [
    path("raw-tune-strings/<int:id>/info", views.RawTuneStringInfoView.as_view(), name="rawtunestring-info")
]