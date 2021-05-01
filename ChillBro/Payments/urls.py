from django.urls import path
from .views import *

urlpatterns = [
    path('myc/update_paid_bookings/', UpdatePaymentDetailsFromMyc.as_view()),
    path('update_cod_bookings/', CODBookingTransactionView.as_view()),
    path('revenue/statistics/details/', GetPaymentsDetailsOfEachEntityView.as_view()),
    path('revenue/statistics/', PaymentRevenueStatisticsView.as_view()),
]
