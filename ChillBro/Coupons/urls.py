from django.urls import path, re_path
from .views import Discount, UseCoupon, CouponList, CouponDetail, CouponHistoryList, AvailableCoupons

urlpatterns = [
    path('discount/', Discount.as_view()),
    path('use_coupon/', UseCoupon.as_view()),
    path('', CouponList.as_view()),
    path('<str:code>/', CouponDetail.as_view()),
    re_path('history/<str:slug>', CouponHistoryList.as_view()),
    path('available/', AvailableCoupons.as_view()),
]
