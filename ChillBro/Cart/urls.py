from django.urls import path
from .views import *


urlpatterns = [
    path('',AddProductToCart.as_view()),
    path('update_product_quantity/', UpdateCartProductQuantity.as_view()),
    path('details/',CartDetails.as_view()),
    path('delete_product/<int:pk>/',DeleteProductFromCart.as_view()),
    path('delete/<str:pk>/',DeleteCart.as_view()),
    path('check_availability_of_all_products/',CheckAvailabilityOfAllProducts.as_view()),
    path('checkout/',CheckoutCart.as_view()),
]