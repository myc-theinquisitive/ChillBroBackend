from django.db import models
import uuid
# Create your models here.
from ChillBro.helpers import get_storage
from .constants import CarouselItemStatus
from .helpers import upload_carousel_image


class Carousel(models.Model):
    name = models.CharField(max_length=30)
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    
    def __str__(self):
        return self.name

class CarouselItem(models.Model):
    carousel = models.ForeignKey('Carousel', on_delete=models.CASCADE)
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    title = models.CharField(max_length=30)
    image = models.ImageField(upload_to=upload_carousel_image,max_length=300, storage=get_storage())
    redirection_url = models.URLField(max_length=256)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[(status.name, status.value) for status in CarouselItemStatus],
                              default=CarouselItemStatus.ACTIVE.value)


class BusinessClientFAQ(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField()


class HelpCenterFAQ(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField()


class HowToUse(models.Model):
    entity_type = models.CharField(max_length=30)
    video_url = models.URLField(max_length=256)
    title = models.CharField(max_length=30)
    short_description = models.TextField()
    content = models.TextField()
