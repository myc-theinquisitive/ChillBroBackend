from django.urls import path
from .views import *


urlpatterns = [
    path('user_details/', UserWishListDetails.as_view()),
    path('add_item/', AddItemToWishList.as_view()),
    path('delete_item/<str:product_id>/', DeleteItemFromWishList.as_view()),
]
