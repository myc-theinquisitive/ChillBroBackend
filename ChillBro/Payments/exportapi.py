from django.core.exceptions import ObjectDoesNotExist
from .constants import PaymentUser, PayStatus
from .serializers import *
from django.conf import  settings
import razorpay


# TODO: should update based on current changes
def transaction_details_by_booking_id(booking_id):
    try:
        transactions = BookingTransaction.objects.get(booking_id=booking_id)
        return BookingTransactionDetailsSerializer(transactions).data
    except ObjectDoesNotExist:
        return {}


def new_booking_transaction(transaction_data):
    booking_id = transaction_data.get('booking_id')
    content = {}
    if transaction_data['paid_by'] == PaymentUser.customer.value and transaction_data['paid_to'] == PaymentUser.myc.value:
        client = razorpay.Client(
            auth=("rzp_test_Ggvw8pTdJ3SnAg", "HQrPh4O1A1bIYP2To2yMjqMJ"))
        content = {
            "amount": float(transaction_data['total_money'])*100,
            "currency": "INR",
        }
        payment = client.order.create(data=content)
        content['callback_url'] = "https://chillbro.co.in/apis/payments/payment_success/"+booking_id+"/" if settings.IS_SERVER else "http://127.0.0.1:8000/payments/payment_success/"+booking_id+"/"
        content['order_id'] = payment['id']
        transaction_data['razorpay_order_id'] = payment['id']

    serializer = BookingTransactionDetailsSerializer()
    serializer.create(transaction_data)
    return content


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
