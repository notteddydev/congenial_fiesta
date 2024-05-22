from celery import shared_task
from django.db import transaction


@shared_task
def tune_update_file_names_for_artist(artist_id):
    print(f"Running tune_update_file_names_for_artist for artist with id: {artist_id}")

    from .models import Tune

    tunes = Tune.objects.filter(artists=artist_id).exclude(file_name__exact="")

    with transaction.atomic():
        for tune in tunes:
            tune.set_file_name()
            tune.save()