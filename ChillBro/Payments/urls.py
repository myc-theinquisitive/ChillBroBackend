from django.urls import path
from .views import *

urlpatterns = [
    path('myc/update_paid_bookings/', UpdatePaymentDetailsFromMyc.as_view()),
    path('update_cod_bookings/', CODBookingTransactionView.as_view()),
    path('revenue/statistics/details/', GetPaymentsRevenueStatisticsDetailsView.as_view()),
    path('revenue/statistics/', PaymentRevenueStatisticsView.as_view()),
    path('refunds/', RefundTransactionList.as_view()),
    path('refunds/<str:pk>/', RefundTransactionDetail.as_view()),
    path('booking_transactions/', GetBookingTransactions.as_view()),
    path('get_specific_transaction/<str:pk>', GetSpecificTransactionDetails.as_view()),
    path('get_transaction_details/',GetTrasactionDetails.as_view()),
]
