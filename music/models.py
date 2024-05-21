import os

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from pydub import AudioSegment
from pytube import YouTube
from pytube.exceptions import VideoUnavailable


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

# @receiver(post_save, dispatch_uid="update_tune_file_names", sender=Artist)
# def update_tune_file_names(sender: Artist, instance: Artist, **kwargs):
#     push job to queue


class Tune(models.Model):
    name = models.CharField(max_length=150)
    file_name = models.CharField(blank=True, editable=False, max_length=200, unique=True)
    artists = models.ManyToManyField(Artist)
    tags = models.ManyToManyField(Tag)
    youtube_id = models.CharField(blank=False, max_length=75, unique=True)

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

        return f"{strTune[:-2]} - {self.name}"

    def get_file_name(self):
        file_name = ''
        artists = Artist.objects.filter(tune=self.id)

        for artist in artists.all():
            file_name += f"{slugify(artist.name)}_and_"

        return f"{file_name[:-5]}-_-{slugify(self.name)}.mp3"

    def download(self):
        try:
            yt = YouTube(self.youtube_link)
        except VideoUnavailable:
            return False

        video = yt.streams.filter(progressive=True).first()
        mp3 = video.download(filename=self.file_name, output_path=os.environ.get('TUNES_DIR'))

        if mp3 is None:
            return False

        song = AudioSegment.from_file(mp3)
        song.export(self.full_file_path, format="mp3")

    class Meta:
        ordering = ["name"]

# @receiver(post_save, dispatch_uid="download_mp3", sender=Tune)
# def download_mp3(sender: Tune, instance: Tune, created: bool, **kwargs):
#     if not created:
#         return

#     push job to queue
