from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class Tag(models.Model):
    name = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(db_index=True, editable=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


@receiver(pre_save, sender=Tag)
def set_slug(sender: Tag, instance: Tag, **kwargs: dict):
    instance.slug = slugify(instance.name)


class Tune(models.Model):
    name = models.CharField(max_length=150)
    file_name = models.CharField(blank=True, editable=False, max_length=200, unique=True)
    tags = models.ManyToManyField(Tag)
    youtube_id = models.CharField(blank=True, max_length=75, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Artist(models.Model):
    name = models.CharField(max_length=150, unique=True)
    tunes = models.ManyToManyField(Tune, through="Participation")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Participation(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    tune = models.ForeignKey(Tune, on_delete=models.CASCADE)
    remixed = models.BooleanField(default=False)
