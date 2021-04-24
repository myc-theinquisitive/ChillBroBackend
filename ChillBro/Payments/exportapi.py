from .models import *
from .serializers import *


def transactionDetailsByBookingId(booking_id):
    try:
        transactions = TransactionDetails.objects.get(booking_id=booking_id)
        return TransactionSerializer(transactions).data
    except:
        return {}
