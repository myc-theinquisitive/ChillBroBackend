from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .constants import CarouselItemStatus
from .views import *

urlpatterns = [
    path('carousel/', CarouselList.as_view()),
    path('carousel/<str:pk>/', CarouselList.as_view()),
    path('carousel/carousel-items/<str:pk>/', CarouselItemsList.as_view()),
    path('carousel-item/', CarouselItemCreate.as_view()),
    path('carousel-item/delete/',  CarouselItemToggle.as_view(), {"status": CarouselItemStatus.DELETED.value}),
    path('carousel-item/active/',  CarouselItemToggle.as_view(), {"status": CarouselItemStatus.ACTIVE.value}),
    path('carousel-item/<str:pk>/', CarouselItemDetail.as_view()),
    path('business-client-faq/',BusinessClientFAQList.as_view()),
    path('business-client-faq/<str:pk>/', BusinessClientFAQDetail.as_view()),
    path('how-to-use/',HowToUseList.as_view()),
    path('how-to-use/entity-type/<str:type>/', HowToUseEntityList.as_view()),
    path('how-to-use/<str:pk>/',HowToUseDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
