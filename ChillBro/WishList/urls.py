from django.urls import path
from .views import *


urlpatterns = [
    path('',CreateWishList.as_view()),
    path('user_wish_list_details/',UserWishListDetails.as_view()),
    path('delete_product_from_wish_list/<int:pk>/',DeletProductFromWishList.as_view()),
]