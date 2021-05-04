from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .constants import Types

from .views import *

urlpatterns = [
    path('credit-amount/', WalletTransactions.as_view(), {"type": Types.CREDIT.value}),
    path('debit-amount/', WalletTransactions.as_view(), {"type": Types.DEBIT.value}),
    path('get-amount/', GetAmount.as_view()),
    path('transaction-history/', TransactionHistory.as_view(), )
]

urlpatterns = format_suffix_patterns(urlpatterns)
