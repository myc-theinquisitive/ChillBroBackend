from django.urls import path
from .views import ReviewRatingList, ReviewRatingDetail, RelatedReviewRatingList, EntityReviewStatistics, \
    EntityTotalReviews, MYCReviewRatingList, CreateFeedbackAndSuggestion, GetFeedbackAndSuggestions

urlpatterns = [
    path('', ReviewRatingList.as_view()),
    path('<int:pk>/', ReviewRatingDetail.as_view()),
    path('<str:related_id>/reviews/', RelatedReviewRatingList.as_view()),
    path('statistics/<str:entity_id>/',EntityReviewStatistics.as_view()),
    path('bookings/<str:entity_id>/',EntityTotalReviews.as_view()),
    path('feedback_and_suggestion/MYC/',CreateFeedbackAndSuggestion.as_view()),
    path('get_feedback_and_suggestions/MYC/',GetFeedbackAndSuggestions.as_view()),
    path('<str:entity_id>/',MYCReviewRatingList.as_view()),
]
