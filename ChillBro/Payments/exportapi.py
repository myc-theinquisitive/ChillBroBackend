from .serializers import *


def transactionDetailsByBookingId(booking_id):
    try:
        transactions = BookingTransaction.objects.get(booking_id=booking_id)
        return TransactionSerializer(transactions).data
    except:
        return {}


def newTransaction(booking_id, entity_id, entity_type, total_money, booking_date, booking_start, paid_to, paid_by):
    transaction = BookingTransaction()
    transaction.booking_id = booking_id
    transaction.entity_id = entity_id
    transaction.entity_type = entity_type
    transaction.total_money = total_money
    transaction.booking_date = booking_date
    transaction.booking_start = booking_start
    transaction.paid_to = paid_to
    transaction.paid_by = paid_by
    return transaction.save()
