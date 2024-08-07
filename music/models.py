import eyed3
import os

from django.db import models
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from pydub import AudioSegment
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from model_utils import FieldTracker
from shutil import copy2, move

from .tasks import tune_download, tune_update_file_name, tune_update_file_names_for_artist
from .utils import get_existing_tune_file_name_by_tune_id


class TuneOrganiser(models.Model):
    @property
    def dir_path(self):
        return f"{os.environ.get('BASE_STORAGE_DIR')}{self.name}"

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ["name"]

class Genre(TuneOrganiser):
    name = models.CharField(max_length=50)

class Tag(TuneOrganiser):
    name = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(db_index=True, editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Artist(TuneOrganiser):
    name = models.CharField(max_length=150, unique=True)

@receiver(post_save, dispatch_uid="update_tune_file_names", sender=Artist)
def update_tune_file_names(sender: Artist, instance: Artist, created: bool, **kwargs):
    if not created:
        transaction.on_commit(lambda: tune_update_file_names_for_artist.delay(instance.id))

class Album(TuneOrganiser):
    name = models.CharField(max_length=100)
    year = models.SmallIntegerField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
    track_count = models.SmallIntegerField(default=1)

    @property
    def is_complete(self):
        return self.track_count == Tune.objects.filter(album__id=self.id).count()

    @property
    def is_single(self):
        return self.track_count == 1
    
    def __str__(self):
        if self.is_complete and not self.is_single:
            return f"{self.name} (Full Album)"
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.replace(" (Single)", "")
        self.name = self.name.replace(" (Remix)", "")

        if self.is_single:
            is_remix = Tune.objects.filter(album__id=self.id, is_remix=True).exists()
            if is_remix:
                self.name = f"{self.name} (Remix)"
            self.name = f"{self.name} (Single)"

        super().save(*args, **kwargs)

    class Meta(TuneOrganiser.Meta):
        unique_together = ('name', 'year', 'artist',)

class RawTuneString(models.Model):
    info = models.CharField(max_length=255)

    def __str__(self):
        return self.info

class Tune(models.Model):
    name = models.CharField(max_length=150)
    file_name = models.CharField(blank=False, editable=False, max_length=200, unique=True)
    artists = models.ManyToManyField(Artist)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    track_number = models.SmallIntegerField(default=1, null=False)
    genre = models.ForeignKey(Genre, on_delete=models.RESTRICT, null=True)
    tags = models.ManyToManyField(Tag)
    youtube_id = models.CharField(blank=False, max_length=75, unique=True)
    trim_start_seconds = models.IntegerField(blank=False, default=0, null=False)
    trim_end_seconds = models.IntegerField(blank=False, default=0, null=False)
    is_remix = models.BooleanField(default=False)
    attempt_download_on_create = models.BooleanField(default=False)

    tracker = FieldTracker()

    @property
    def youtube_link(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"
    
    @property
    def full_file_path_original(self):
        return f"{os.environ.get('ORIGINAL_TUNES_DIR')}/{self.file_name}"

    @property
    def full_file_path(self):
        return f"{os.environ.get('TUNES_DIR')}/{self.file_name}"

    @property
    def downloaded(self):
        return os.path.isfile(self.full_file_path)
    
    @property
    def trimmable(self):
        return self.trim_end_seconds + self.trim_start_seconds > 0

    def __str__(self):
        return f"{self.name} - {self.id}"

    def save(self, *args, **kwargs):
        if self.file_name == "":
            self.file_name = f"{self.youtube_id}.mp3"

        self.name = self.name.replace(" (Remix)", "")
        if self.is_remix:
            self.name = f"{self.name} (Remix)"            

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.remove_files()
        super().delete(*args, **kwargs)

    def set_file_name(self):
        file_name = ''
        artists = Artist.objects.filter(tune=self.id)

        for artist in artists.all():
            file_name += f"{slugify(artist.name)}_and_"

        self.file_name = f"{file_name[:-5]}-_-{slugify(self.name)}-_-{self.id}.mp3"

        return self
    
    def move_files(self):
        existing_file_name = get_existing_tune_file_name_by_tune_id(self.id)

        current_path = f"{os.environ.get('TUNES_DIR')}/{existing_file_name}"
        current_original_path = f"{os.environ.get('ORIGINAL_TUNES_DIR')}/{existing_file_name}"

        move(current_path, self.full_file_path)
        move(current_original_path, self.full_file_path_original)
    
    def remove_files(self):
        if self.downloaded:
            os.remove(self.full_file_path)
            os.remove(self.full_file_path_original)

    def trim(self):
        if not self.trimmable:
            return

        ms_end = self.trim_end_seconds * 1000
        ms_start = self.trim_start_seconds * 1000

        song = AudioSegment.from_file(self.full_file_path_original)

        if ms_end > 0:
            song = song[:-ms_end]

        if ms_start > 0:
            song = song[ms_start:]

        song.export(self.full_file_path, format="mp3")


    def download(self):
        try:
            yt = YouTube(self.youtube_link)
        except VideoUnavailable:
            return False

        try:
            video = yt.streams.filter(progressive=True).first()
        except AttributeError:
            return False
        
        mp3 = video.download(filename=self.file_name, output_path=os.environ.get("ORIGINAL_TUNES_DIR"))

        if mp3 is None:
            return False

        song = AudioSegment.from_file(mp3)
        song.export(self.full_file_path_original, format="mp3")
        if self.trimmable:
            self.trim()
        else:
            copy2(self.full_file_path_original, self.full_file_path)

        return True
    
    def set_metadata(self):
        audiofile = eyed3.load(self.full_file_path)
        audiofile.tag.album = self.album.name
        audiofile.tag.album_artist = self.album.artist.name
        audiofile.tag.artist = ", ".join([artist.name for artist in self.artists.all()])
        audiofile.tag.comments.set(f"id={self.id}")
        audiofile.tag.genre = self.genre.name
        audiofile.tag.recording_date = self.album.year
        audiofile.tag.title = self.name
        audiofile.tag.track_num = self.track_number
        audiofile.tag.save()

    class Meta:
        ordering = ["name"]
        unique_together = ('album', 'track_number',)

@receiver(post_save, dispatch_uid="download_tune", sender=Tune)
def download_tune(sender: Tune, instance: Tune, created: bool, **kwargs):
    if created:
        if instance.attempt_download_on_create:
            transaction.on_commit(lambda: tune_download.delay(instance.id))
    elif instance.tracker.has_changed('name'):
        transaction.on_commit(lambda: tune_update_file_name.delay(instance.id))