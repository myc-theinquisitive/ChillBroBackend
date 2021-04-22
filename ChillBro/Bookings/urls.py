from django.urls import path
from .views import *
from .RentalCalendar.views import*


urlpatterns = [

    path('',OrdersList.as_view()),
    path('orderedproducts',OrderedProductsList.as_view()),
    path('<int:pk>',OrderDeleteList.as_view()),
    path('userorders',UserOrdersList.as_view()),
    path('update_booking_status',UpdateBookingStatusView.as_view()),
    path('orderdetails',OrderDetailsListFilter.as_view()),
    path('cancel_order', CancelOrderView.as_view()),
    path('statistics',BookingsStatistics.as_view()),
    path('get_statistics_details',GetBookingsStatisticsDetails.as_view()),
    path('update_product_status', UpdateProductStatusView.as_view()),
    path('payments/revenue/statistics', PaymentRevenueStatisticsView.as_view()),
    path('date_filters/',dateFilters),
    path('business_client/<str:booking_id>', GetSpecificBookingDetails.as_view()),
    path('details',GetBookingDetailsView.as_view()),
    path('start/', BookingStart.as_view()),
    path('end/',BookingEnd.as_view()),
    path('end/<str:booking_id>',BookingEndBookingIdDetialsView.as_view()),
    path('reviews/report_customer/',ReviewsBookingsOnReportCustomerList.as_view()),
    path('payments/<str:entity_id>',GetPaymentsDetailsOfEachEntityView.as_view()),
    path('generate_pdf',GeneratePDF.as_view()),
    path('generate_excel',generate_excel),
    path('product/<str:product_id>',GetBookingDetailsOfProductId.as_view()),


    path('add', CreateUpdateRentalBooking.as_view()),
    path('get_all/', RentalBookingList.as_view()),
    path('cancel_booking/', CancelRentalBooking.as_view()),
    path('product_availability/', GetProductAvailability.as_view()),
    path('product/bookings/', ProductBookingList.as_view()),
    path('product/cancelled_bookings/', CancelledBookingList.as_view()),

]

