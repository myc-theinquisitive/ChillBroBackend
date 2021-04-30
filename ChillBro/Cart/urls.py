from django.urls import path
from .views import *


urlpatterns = [
    path('',CreateCart.as_view()),
    path('update_cart_product_quantity/', UpdateCartProductQuantity.as_view()),
    path('cart_details/',CartDetails.as_view()),
    path('delete_product_from_cart/<int:pk>/',DeleteProductFromCart.as_view()),
    path('delete_cart/<str:pk>/',DeleteCart.as_view()),
    path('check_availability_of_all_products/',CheckAvailabilityOfAllProducts.as_view()),
]