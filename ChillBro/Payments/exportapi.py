from .serializers import *


# TODO: should update based on current changes
def transaction_details_by_booking_id(booking_id):
    try:
        transactions = BookingTransaction.objects.get(booking_id=booking_id)
        return BookingTransactionDetailsSerializer(transactions).data
    except:
        return {}


def new_transaction(transaction_data):
    serializer = BookingTransactionDetailsSerializer()
    serializer.create(transaction_data)
    return True
