from django.contrib import admin
from .models import ReviewsRatings
# Register your models here.
@admin.register(ReviewsRatings)
class ReviewsRatingsAdmin(admin.ModelAdmin):
    pass