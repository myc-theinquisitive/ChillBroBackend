from django.urls import path
from .views import *


urlpatterns = [
    path('',CreateWishList.as_view()),
    path('user_details/',UserWishListDetails.as_view()),
    path('delete_product/<str:pk>/',DeletProductFromWishList.as_view()),
]