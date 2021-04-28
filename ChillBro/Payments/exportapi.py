from .models import *
from .serializers import *


def transaction_details_by_booking_id(booking_id):
    try:
        transactions = TransactionDetails.objects.get(booking_id=booking_id)
        return TransactionSerializer(transactions).data
    except:
        return {}


def new_transaction(booking_id, entity_id, entity_type, total_money, payment_status, booking_date,total_net_value):
    transaction = TransactionDetails()
    transaction.booking_id = booking_id
    transaction.entity_id = entity_id
    transaction.entity_type = entity_type
    transaction.total_money = total_money
    transaction.total_net_value = total_net_value
    transaction.payment_status = payment_status
    transaction.booking_date = booking_date
    return transaction.save()