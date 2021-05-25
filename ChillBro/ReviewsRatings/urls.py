from django.urls import path
from .views import ReviewRatingList, ReviewRatingDetail, RelatedReviewRatingList, EntityReviewStatistics, \
    EntityTotalReviews, EntityReviewRatingList, CreateFeedbackAndSuggestion, GetFeedbackAndSuggestions, \
    GetBusinessCleintToMYCReview

urlpatterns = [
    path('', ReviewRatingList.as_view()),
    path('<int:pk>/', ReviewRatingDetail.as_view()),
    path('<str:related_id>/reviews/', RelatedReviewRatingList.as_view()),
    path('get_business_cleint/MYC/',GetBusinessCleintToMYCReview.as_view()),
    path('statistics/',EntityReviewStatistics.as_view()),
    path('get_total_reviews/',EntityTotalReviews.as_view()),
    path('feedback_and_suggestion/MYC/',CreateFeedbackAndSuggestion.as_view()),
    path('get_feedback_and_suggestions/MYC/',GetFeedbackAndSuggestions.as_view()),
    path('<str:entity_id>/', EntityReviewRatingList.as_view()),
]
