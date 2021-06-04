from .views import *
from django.urls import path

urlpatterns = [
    path('send/',sendNotification.as_view()),
    path('create/',NotificationCreate.as_view()),
    path('business_client/',BusinessClientNotification.as_view()),
    path('business_client/<str:type>/', BusinessClientTypeNotification.as_view()),
    path('users/', UserNotification.as_view()),
    path('users/<str:type>/', UserTypeNotification.as_view()),
    path('delete/',DeleteNotification.as_view()),
    path('change-setting/',ChangeSetting.as_view()),
    path('firebase_token/',AddOrUpdateFirebaseToken.as_view()),
]

