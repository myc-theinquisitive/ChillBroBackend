from django.contrib import admin
from .models import ReviewsRatings, FeedbackAndSuggestions
# Register your models here.


@admin.register(ReviewsRatings)
@admin.register(FeedbackAndSuggestions)
class ReviewsRatingsAdmin(admin.ModelAdmin):
    pass