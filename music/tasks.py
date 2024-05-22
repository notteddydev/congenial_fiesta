import os
from shutil import move

from celery import shared_task
from django.db import IntegrityError, transaction
from django.db.models import F

from .utils import get_existing_tune_file_name_by_tune_id


@shared_task
def tune_download(tune_id):
    print(f"Running tune_download for tune with id: {tune_id}")

    from .models import Tune
    
    tune = Tune.objects.get(pk=tune_id)
    tune.set_file_name()
    if tune.download():
        tune.save()


@shared_task
def tune_update_file_name(tune_id):
    print(f"Running tune_update_file_name for tune with id: {tune_id}")

    from .models import Tune

    tune = Tune.objects.get(pk=tune_id)
    existing_file_name = get_existing_tune_file_name_by_tune_id(tune_id)

    if existing_file_name is None:
        tune.file_name = f"{tune.youtube_id}.mp3"
        tune.save()
        return
     
    tune.set_file_name().save()
    current_path = f"{os.environ.get('TUNES_DIR')}/{existing_file_name}"

    move(current_path, tune.full_file_path)


@shared_task
def tune_update_file_names_for_artist(artist_id):
    print(f"Running tune_update_file_names_for_artist for artist with id: {artist_id}")

    from .models import Tune

    # Don't rename tune.file_name where the file_name is "{tune.youtube_id}.mp3"
    # because that means that the tune hasn't been downloaded yet, and after the 
    # download the file_name is set properly anyway.
    tunes = Tune.objects.filter(artists=artist_id).exclude(file_name__startswith=F('youtube_id'))

    try:
        with transaction.atomic():
            for tune in tunes:
                tune.set_file_name().save()
    except IntegrityError:
        raise IntegrityError(f"Tunes couldn't be updated for artist with id: {artist_id}")
    
    # Could this be done in the transaction.atomic() block?
    for tune in tunes:
        existing_file_name = get_existing_tune_file_name_by_tune_id(tune.id)

        if existing_file_name is None:
            print(f"No file found for tune with id: {tune.id}")
            continue

        current_path = f"{os.environ.get('TUNES_DIR')}/{existing_file_name}"
        move(current_path, tune.full_file_path)