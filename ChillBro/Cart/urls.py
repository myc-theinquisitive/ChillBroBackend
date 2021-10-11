from django.urls import path
from .views import *
# from .add_product_to_cart import

urlpatterns = [
    path('',AddProductToCart.as_view()),
    path('update_product/', UpdateCartProduct.as_view()),
    path('details/<str:entity_type>/',CartDetails.as_view()),
    path('delete_product/<int:pk>/',DeleteProductFromCart.as_view()),
    path('delete/<str:pk>/',DeleteCart.as_view()),
    path('check_availability/',CheckAvailability.as_view()),
    path('check_availability_of_all_products/<str:entity_type>/',CheckAvailabilityOfAllProducts.as_view()),
    path('checkout/',CheckoutCart.as_view()),
    path('multiple_bookings/',AddMultipleBookings.as_view()),
]