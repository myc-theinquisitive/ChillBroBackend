from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('', EntityList.as_view(), name='new_entity'),
    path('business_client/all/status/', EntityStatusAll.as_view(), name='entity_status_all'),
    path('<str:pk>/status/',EntityStatus.as_view(), name='entity_status'),
    path('business_client/',BusinessClientEntityList.as_view(),name='business_client_list'),
    path('business_client/<str:pk>/', BusinessClientEntityDetail.as_view(),name='business_client_detail'),
    path('<str:bc_id>/outlets/',BusinessClientOutlets.as_view(),name='business_client_outlets'),
    path('share_app/',ShareApp),


    path('<str:pk>/', EntityDetail.as_view(), name='entity_detail'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
