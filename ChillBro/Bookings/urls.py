from django.urls import path

from .views import *
from .RentalCalendar.views import*


urlpatterns = [

    path('',OrdersList.as_view()),
    path('orderedproducts',OrderedProductsList.as_view()),
    path('<int:pk>',OrderDeleteList.as_view()),
    path('userorders',UserOrdersList.as_view()),
    path('cancelorder',CancelOrderList.as_view()),
    path('orderdetails',OrderDetailsListFilter.as_view()),
    path('statistics',BookingsStatistics.as_view()),


    path('add', CreateUpdateRentalBooking.as_view()),
    path('get_all/', RentalBookingList.as_view()),
    path('cancel_booking/', CancelRentalBooking.as_view()),
    path('product_availability/', GetProductAvailability.as_view()),
    path('product/bookings/', ProductBookingList.as_view()),
    path('product/cancelled_bookings/', CancelledBookingList.as_view()),

]

