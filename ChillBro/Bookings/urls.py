from django.urls import path
from .views import *
from .RentalCalendar.views import*


urlpatterns = [

    # urls for category
    # path('category/', CategoryList.as_view()),
    path('',OrdersList.as_view()),
    path('orderedproducts',OrderedProductsList.as_view()),
    path('<int:pk>',OrderDeleteList.as_view()),
    path('userorders',UserOrdersList.as_view()),
    path('cancelorder',CancelOrderList.as_view()),
    path('orderdetails',OrderDetailsList.as_view()),


    path('rental_calendar/', CreateUpdateRentalBooking.as_view()),
    path('rental_calendar/get_all/', RentalBookingList.as_view()),
    path('rental_calendar/cancel_booking/', CancelRentalBooking.as_view()),
    path('rental_calendar/product_availability/', GetProductAvailability.as_view()),
    path('rental_calendar/product/bookings/', ProductBookingList.as_view()),
    path('rental_calendar/product/cancelled_bookings/', CancelledBookingList.as_view()),

]

