from django.urls import path
from .views import CreateUpdateRentalBooking, CancelRentalBooking, RentalBookingList, GetProductAvailability, \
    ProductBookingList, CancelledBookingList

urlpatterns = [
    path('', CreateUpdateRentalBooking.as_view()),
    path('get_all/', RentalBookingList.as_view()),
    path('cancel_booking/', CancelRentalBooking.as_view()),
    path('product_availability/', GetProductAvailability.as_view()),
    path('product/bookings/', ProductBookingList.as_view()),
    path('product/cancelled_bookings/', CancelledBookingList.as_view()),
]

