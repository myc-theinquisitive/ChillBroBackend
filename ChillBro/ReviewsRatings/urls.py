from django.urls import path
from .views import ReviewRatingList, ReviewRatingDetail, RelatedReviewRatingList, EntityReviewStatistics, \
    EntityTotalReviews, EntityReviewRatingList, CreateBCAppFeedbackAndSuggestion, GetBCAppFeedbackAndSuggestions, \
    GetBusinessCleintToMYCReview, CreateCustomerAppFeedbackAndSuggestion, GetCustomerAppFeedbackAndSuggestions, \
    CustomerAppRatingList, GetCustomerAppLastRatingForUser, BCAppRatingList, GetBCAppLastRatingForUser

urlpatterns = [
    path('', ReviewRatingList.as_view()),
    path('<str:related_id>/reviews/', RelatedReviewRatingList.as_view()),
    path('get_business_cleint/MYC/', GetBusinessCleintToMYCReview.as_view()),
    path('statistics/', EntityReviewStatistics.as_view()),
    path('get_total_reviews/', EntityTotalReviews.as_view()),
    path('bc_app_feedback_and_suggestion/', CreateBCAppFeedbackAndSuggestion.as_view()),
    path('get_all_bc_app_feedback_and_suggestions/', GetBCAppFeedbackAndSuggestions.as_view()),
    path('customer_app_feedback_and_suggestion/', CreateCustomerAppFeedbackAndSuggestion.as_view()),
    path('get_all_customer_app_feedback_and_suggestions/', GetCustomerAppFeedbackAndSuggestions.as_view()),
    path('customer_app_rating/', CustomerAppRatingList.as_view()),
    path('customer_app_rating/user/latest/', GetCustomerAppLastRatingForUser.as_view()),
    path('bc_app_rating/', BCAppRatingList.as_view()),
    path('bc_app_rating/user/latest/', GetBCAppLastRatingForUser.as_view()),
    path('<int:pk>/', ReviewRatingDetail.as_view()),
    path('entity/<str:entity_id>/', EntityReviewRatingList.as_view()),
]
