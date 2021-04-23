from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('business_client/',ReferBusinessClientList.as_view()),
    path('business_client/<str:pk>/',ReferBusinessClientDetail.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns)
