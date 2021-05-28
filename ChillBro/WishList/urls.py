from django.urls import path
from .views import *


urlpatterns = [
    path('user/', UserWishListDetails.as_view()),
    path('add/product/', AddProductToWishList.as_view()),
    path('delete/product/<str:product_id>/', DeleteProductFromWishList.as_view()),
    path('add/entity/', AddEntityToWishList.as_view()),
    path('delete/entity/<str:entity_id>/', DeleteEntityFromWishList.as_view()),
]
