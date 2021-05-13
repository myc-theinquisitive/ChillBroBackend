from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('', EntityList.as_view(), name='new_entity'),
    path('verification/<str:entity_id>/', EntityVerificationDetail.as_view(), name='entity_verification_detail'),
    path('verification_status/<str:status>/', EntityListBasedOnVerificationStatus.as_view()),
    path('business_client/all/status/', EntityStatusAll.as_view(), name='entity_status_all'),
    path('<str:pk>/status/', EntityStatus.as_view(), name='entity_status'),
    path('business_client/count/', CountOfEntitiesAndProducts.as_view()),
    path('business_client/all-entities/', BusinessClientEntities.as_view(), name='business_client_outlets'),
    path('<str:pk>/', EntityDetail.as_view(), name='entity_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
