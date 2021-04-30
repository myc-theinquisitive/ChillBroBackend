from .models import *
from .serializers import *


def transactionDetailsByBookingId(booking_id):
    try:
        transactions = TransactionDetails.objects.get(booking_id=booking_id)
        return TransactionSerializer(transactions).data
    except:
        return {}


def newTransaction(booking_id, entity_id, entity_type, total_money, booking_date):
    transaction = TransactionDetails()
    transaction.booking_id = booking_id
    transaction.entity_id = entity_id
    transaction.entity_type = entity_type
    transaction.total_money = total_money
    transaction.booking_date = booking_date
    return transaction.save()