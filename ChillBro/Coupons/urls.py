from django.urls import path
from .views import Discount, UseCoupon

urlpatterns = [
    path('discount/', Discount.as_view()),
    path('use_coupon/', UseCoupon.as_view()),
]
