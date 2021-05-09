from django.urls import path
from .views import ReportCustomerReasonsList, ReportCustomerReasonsDetail, CreateBooking, UserBookingsList, \
    CancelBookingView, BookingsStatistics, GetBookingsStatisticsDetails, CancelProductStatusView, GetDateFilters, \
    GetSpecificBookingDetails, GetBookingDetailsView, BookingStart, BookingEnd, GetBookingEndDetailsView, \
    ReportCustomerForBooking, GeneratePDF, GenerateExcel, GetBookingDetailsOfProductId, ProductStatistics, \
    GetProductAvailability, BusinessClientProductCancellationDetails


urlpatterns = [
    path('create_report_customer_reason/', ReportCustomerReasonsList.as_view()),
    path('detail_report_customer_reason/<int:pk>/', ReportCustomerReasonsDetail.as_view()),
    path('', CreateBooking.as_view()),
    path('user_bookings/', UserBookingsList.as_view()),
    path('cancel_booking/<str:booking_id>/', CancelBookingView.as_view()),
    path('statistics/', BookingsStatistics.as_view()),
    path('get_statistics_details/', GetBookingsStatisticsDetails.as_view()),
    path('cancel_product/', CancelProductStatusView.as_view()),
    path('date_filters/', GetDateFilters.as_view()),
    path('business_client/<str:booking_id>/', GetSpecificBookingDetails.as_view()),
    path('details/', GetBookingDetailsView.as_view()),
    path('start/', BookingStart.as_view()),
    path('end/', BookingEnd.as_view()),
    path('end/<str:booking_id>/', GetBookingEndDetailsView.as_view()),
    path('report_customer/', ReportCustomerForBooking.as_view()),
    path('generate_pdf/', GeneratePDF.as_view()),
    path('generate_excel/', GenerateExcel.as_view()),
    path('product/<str:product_id>/', GetBookingDetailsOfProductId.as_view()),
    path('product_statistics/<str:product_id>/', ProductStatistics.as_view()),
    path('product_availability/', GetProductAvailability.as_view()),
    path('back_to_online/add/', BusinessClientProductCancellationDetails.as_view()),
]
