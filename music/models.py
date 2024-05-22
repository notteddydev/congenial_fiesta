import os
import eyed3

from django.db import models
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from pydub import AudioSegment
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from model_utils import FieldTracker

from .tasks import tune_download, tune_update_file_name, tune_update_file_names_for_artist


class Tag(models.Model):
    name = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(db_index=True, editable=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]


class Artist(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

@receiver(post_save, dispatch_uid="update_tune_file_names", sender=Artist)
def update_tune_file_names(sender: Artist, instance: Artist, created: bool, **kwargs):
    if not created:
        transaction.on_commit(lambda: tune_update_file_names_for_artist.delay(instance.id))


class Tune(models.Model):
    name = models.CharField(max_length=150)
    file_name = models.CharField(blank=False, editable=False, max_length=200, unique=True)
    artists = models.ManyToManyField(Artist)
    tags = models.ManyToManyField(Tag)
    youtube_id = models.CharField(blank=False, max_length=75, unique=True)

    tracker = FieldTracker()

    @property
    def youtube_link(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"

    @property
    def full_file_path(self):
        return f"{os.environ.get('TUNES_DIR')}/{self.file_name}"

    @property
    def downloaded(self):
        if len(self.file_name) == 0:
            return False

        if not os.path.isdir(os.environ.get('TUNES_DIR')):
            return False

        if not self.file_name in os.listdir(os.environ.get('TUNES_DIR')):
            return False

        return True

    def __str__(self):
        strTune = ''

        for artist in self.artists.all():
            strTune += f"{artist.name}, "

        return f"{self.name} - {strTune[:-2]}"

    def save(self, *args, **kwargs):
        if self.file_name == "":
            self.file_name = f"{self.youtube_id}.mp3"

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.remove_file()
        super().delete(*args, **kwargs)

    def set_file_name(self):
        file_name = ''
        artists = Artist.objects.filter(tune=self.id)

        for artist in artists.all():
            file_name += f"{slugify(artist.name)}_and_"

        self.file_name = f"{file_name[:-5]}-_-{slugify(self.name)}-_-{self.id}.mp3"

        return self
    
    def remove_file(self):
        if os.path.isfile(self.full_file_path):
            os.remove(self.full_file_path)

    def download(self):
        try:
            yt = YouTube(self.youtube_link)
        except VideoUnavailable:
            return False

        try:
            video = yt.streams.filter(progressive=True).first()
        except AttributeError:
            return False
        
        mp3 = video.download(filename=self.file_name, output_path=os.environ.get("TUNES_DIR"))

        if mp3 is None:
            return False

        song = AudioSegment.from_file(mp3)
        song.export(self.full_file_path, format="mp3")

        return True
    
    def set_metadata(self):
        audiofile = eyed3.load(self.full_file_path)
        audiofile.tag.artist = ", ".join(list(Artist.objects.filter(tune=self.id).values("name")))
        audiofile.tag.title = self.name
        audiofile.tag.save()
        

    class Meta:
        ordering = ["name"]

@receiver(post_save, dispatch_uid="download_tune", sender=Tune)
def download_tune(sender: Tune, instance: Tune, created: bool, **kwargs):
    if created:
        transaction.on_commit(lambda: tune_download.delay(instance.id))
    elif instance.tracker.has_changed('name'):
        transaction.on_commit(lambda: tune_update_file_name.delay(instance.id))