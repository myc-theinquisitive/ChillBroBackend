from django.db import models
import uuid
from .helpers import upload_image_to_place
from django.db.models import Q


def get_id():
    return str(uuid.uuid4())


class PlaceManager(models.Manager):

    def search(self, query):
        lookups = (Q(name__icontains=query) |
                   Q(description__icontains=query))
        return self.filter(lookups).distinct()


class Place(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
    address_id = models.CharField(max_length=36)

    objects = PlaceManager()

    def __str__(self):
        return self.name + "-" + self.category.name

    class Meta:
        unique_together = ('name', 'category')


class PlaceImage(models.Model):
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_to_place)
    order = models.IntegerField()

    class Meta:
        unique_together = ('place', 'order',)
        ordering = ['order']

    def __str__(self):
        return "Place Image - {0}".format(self.id)
