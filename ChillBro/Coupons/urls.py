from django.urls import path
from .views import Discount, UseCoupon, CouponList, CouponDetail, CouponHistoryList, AvailableCoupons

urlpatterns = [
    path('discount/', Discount.as_view()),
    path('use_coupon/', UseCoupon.as_view()),
    path('', CouponList.as_view()),
    path('<int:pk>/', CouponDetail.as_view()),
    path('history/', CouponHistoryList.as_view()),
    path('available/', AvailableCoupons.as_view()),
]
