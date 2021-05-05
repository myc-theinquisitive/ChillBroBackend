from django.urls import path
from .models import *
from .views import *

urlpatterns = [

    path('create/', CreateBookingTransaction.as_view()),
    path('<str:entity_id>/', GetPaymentsDetailsOfEachEntityView.as_view()),
    path('revenue/statistics/', PaymentRevenueStatisticsView.as_view()),
]


