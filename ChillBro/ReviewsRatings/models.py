from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import datetime
from ChillBro.helpers import get_storage
from .constants import REVIEW_SCALE, BCAppFeedbackCategory, BASE_RATING_STRING
from .helpers import image_upload_to_review


class ReviewsRatings(models.Model):
    # main id for which rating is given
    related_id = models.CharField(max_length=36, verbose_name="Related Id")
    # secondary id for which the rating is linked too
    secondary_related_id = models.CharField(max_length=36, null=True, blank=True, default=None)
    # For location, service etc..
    rating_type = models.CharField(default=BASE_RATING_STRING, max_length=30)
    comment = models.TextField(verbose_name="Comment")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(REVIEW_SCALE)])
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Reviewed By")
    reviewed_time = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return "Related Id - {0} Rating - {1}".format(self.related_id, self.rating)

    class Meta:
        unique_together = ('related_id', 'secondary_related_id', 'rating_type', 'created_by',)


class ReviewImage(models.Model):
    review = models.ForeignKey("ReviewsRatings", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_review, max_length=300, storage=get_storage())

    def __str__(self):
        return "Review Image - {0}".format(self.id)


class BCAppFeedbackAndSuggestions(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Reviewed By")
    opinion = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(REVIEW_SCALE)])
    category = models.CharField(max_length=30, choices=
        [(category_type.value, category_type.value) for category_type in BCAppFeedbackCategory],
                                default=BCAppFeedbackCategory.suggestion.value)
    comment = models.TextField()
    submitted_on = models.DateTimeField(default=datetime.now)


class CustomerAppFeedbackAndSuggestions(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Reviewed By")
    category = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    comment = models.TextField()
    submitted_on = models.DateTimeField(default=datetime.now)


class CustomerAppRating(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Reviewed By")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(REVIEW_SCALE)])
    comment = models.TextField()
    submitted_on = models.DateTimeField(default=datetime.now)


class BCAppRating(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Reviewed By")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(REVIEW_SCALE)])
    comment = models.TextField()
    submitted_on = models.DateTimeField(default=datetime.now)
