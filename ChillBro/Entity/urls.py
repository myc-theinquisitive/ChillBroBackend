from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('', EntityList.as_view(), name='new_entity'),
    path('image/', EntityImageCreate.as_view()),
    path('image/<int:pk>/', EntityImageDelete.as_view()),

    # urls for amenities
    path('amenities/', AmenitiesList.as_view()),

    # hotel home page entities
    path('hotel_home_page_categories/', HotelHomePageCategories.as_view()),

    # urls for verification
    path('verification/<str:entity_id>/', EntityVerificationDetail.as_view(), name='entity_verification_detail'),
    path('verification_status/<str:status>/', EntityListBasedOnVerificationStatus.as_view()),

    # urls for status
    path('all/status/', EntityStatusAll.as_view(), name='entity_status_all'),
    path('<str:pk>/status/', EntityStatus.as_view(), name='entity_status'),

    # urls for registration
    path('account-details/<str:pk>/', EntityAccountDetail.as_view(), name='entity_account'),
    path('upi-details/<str:pk>/', EntityUPIDetail.as_view(), name='entity_upi'),
    path('registration-details/<str:pk>/', EntityRegistrationDetail.as_view(), name='entity_registration'),
    path('basic-details/<str:pk>/', EntityBasicDetail.as_view(), name='entity_basic'),

    # urls for business client
    path('business_client/count/', CountOfEntitiesAndProducts.as_view()),
    path('business_client/all-entities/', BusinessClientEntities.as_view(), name='business_client_outlets'),
    path('business_client/entities/type-wise/', BusinessClientEntitiesByType.as_view(),
         name='business_client_outlets_type_wise'),
    path('business_client/verification_status/', BusinessClientEntitiesByVerificationStatus.as_view()),
    path('<str:pk>/', EntityDetail.as_view(), name='entity_detail'),

    # urls for user
    path('category/<str:slug>/', GetEntitiesBySubType.as_view()),
    path('user/<str:pk>/', GetEntitiesDetailsForUser.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
