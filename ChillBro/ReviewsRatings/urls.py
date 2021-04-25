from django.urls import path
from .views import ReviewRatingList, ReviewRatingDetail, RelatedReviewRatingList

urlpatterns = [
    path('', ReviewRatingList.as_view()),
    path('<int:pk>/', ReviewRatingDetail.as_view()),
    path('<str:related_id>/reviews/', RelatedReviewRatingList.as_view()),
]
