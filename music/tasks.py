import os
from shutil import move

from celery import shared_task
from django.db import IntegrityError, transaction
from django.db.models import F

from .utils import get_tune_id_from_file_name


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

    tune_file_names = os.listdir(os.environ.get('TUNES_DIR'))

    tune_gen = (
        tune_file_name for tune_file_name in tune_file_names
        if tune_id == get_tune_id_from_file_name(tune_file_name)
    )
    existing_file_name = next(tune_gen, None)

    if existing_file_name is None:
        tune.file_name = f"{tune.youtube_id}.mp3"
        tune.save()
        return
     
    tune.set_file_name().save()
    current_file_path = f"{os.environ.get('TUNES_DIR')}/{existing_file_name}"
    new_file_path = f"{os.environ.get('TUNES_DIR')}/{tune.file_name}"
    move(current_file_path, new_file_path)


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

    tune_file_names = os.listdir(os.environ.get('TUNES_DIR'))

    for tune_file_name in tune_file_names:
        current_path = f"{os.environ.get('TUNES_DIR')}/{tune_file_name}"
        tune_id = get_tune_id_from_file_name(tune_file_name)
        tune = tunes.get(pk=tune_id)

        new_path = f"{os.environ.get('TUNES_DIR')}/{tune.file_name}"

        move(current_path, new_path)