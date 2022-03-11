from django.contrib import admin
from .models import ReviewsRatings, BCAppFeedbackAndSuggestions
# Register your models here.


@admin.register(ReviewsRatings)
@admin.register(BCAppFeedbackAndSuggestions)
class ReviewsRatingsAdmin(admin.ModelAdmin):
    pass