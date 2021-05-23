from django.urls import path
from .views import *


urlpatterns = [
    path('',AddProductToWishList.as_view()),
    path('user_details/',UserWishListDetails.as_view()),
    path('delete_product/<str:product_id>/', DeleteProductFromWishList.as_view()),
]