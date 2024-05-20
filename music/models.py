from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


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
def update_tune_file_names(sender: Artist, instance: Artist, **kwargs):
    tunes = Tune.objects.filter(artists__id=instance.id)

    for tune in tunes:
        tune.save()


class Tune(models.Model):
    name = models.CharField(max_length=150)
    file_name = models.CharField(blank=True, editable=False, max_length=200, unique=True)
    artists = models.ManyToManyField(Artist)
    tags = models.ManyToManyField(Tag)
    youtube_id = models.CharField(blank=True, max_length=75, unique=True)

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

        return f"{file_name[:-5]}-_-{slugify(self.name)}"
    
    def save(self, *args, **kwargs):
        self.file_name = self.get_file_name()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]