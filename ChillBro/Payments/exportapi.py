from django.core.exceptions import ObjectDoesNotExist
from .constants import PaymentUser, PayStatus
from .serializers import *


# TODO: should update based on current changes
def transaction_details_by_booking_id(booking_id):
    try:
        transactions = BookingTransaction.objects.get(booking_id=booking_id)
        return BookingTransactionDetailsSerializer(transactions).data
    except ObjectDoesNotExist:
        return {}


def new_booking_transaction(transaction_data):
    serializer = BookingTransactionDetailsSerializer()
    serializer.create(transaction_data)
    return True


def new_refund_transaction(transaction_data):
    serializer = RefundTransactionDetailsSerializer()
    serializer.create(transaction_data)
    return True


def update_booking_transaction(booking_id, is_complete_cancellation, total_amount_reduced,
                               net_amount_reduced, commission_amount_reduced):

    if is_complete_cancellation:
        BookingTransaction.objects.filter(booking_id=booking_id).update(payment_status=PayStatus.cancelled.value)
        return True

    # transaction from MYC to Entity
    BookingTransaction.objects.filter(booking_id=booking_id, paid_by=PaymentUser.myc.value,
                                      paid_to=PaymentUser.entity.value)\
        .update(total_money=F('total_money') - net_amount_reduced)

    # transaction from Customer to Entity
    BookingTransaction.objects.filter(booking_id=booking_id, paid_by=PaymentUser.customer.value,
                                      paid_to=PaymentUser.entity.value) \
        .update(total_money=F('total_money') - total_amount_reduced)

    # transaction from Entity to MYC
    BookingTransaction.objects.filter(booking_id=booking_id, paid_by=PaymentUser.entity.value,
                                      paid_to=PaymentUser.myc.value) \
        .update(total_money=F('total_money') - commission_amount_reduced)
