from celery import shared_task
from django.db import transaction
from django.db.models import F


@shared_task
def tune_update_file_names_for_artist(artist_id):
    print(f"Running tune_update_file_names_for_artist for artist with id: {artist_id}")

    from .models import Tune

    # Don't rename tune.file_name where the file_name is "{tune.youtube_id}.mp3"
    # because that means that the tune hasn't been downloaded yet, and after the 
    # download the file_name is set properly anyway.
    tunes = Tune.objects.filter(artists=artist_id).exclude(file_name__startswith=F('youtube_id'))

    with transaction.atomic():
        for tune in tunes:
            tune.set_file_name().save()

    