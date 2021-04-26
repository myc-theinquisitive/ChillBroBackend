from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .helpers import image_upload_to_review


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReviewsRatings(models.Model):
    related_id = models.CharField(max_length=36, verbose_name="Related Id")
    comment = models.TextField(verbose_name="Comment")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user_model = get_user_model()
    reviewed_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Reviewed By")

    def __str__(self):
        return "Related Id - {0} Rating - {1}".format(self.related_id, self.rating)

    class Meta:
        unique_together = ('related_id', 'reviewed_by',)


class ReviewImage(models.Model):
    review = models.ForeignKey("ReviewsRatings", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_review)

    def __str__(self):
        return "Review Image - {0}".format(self.id)
