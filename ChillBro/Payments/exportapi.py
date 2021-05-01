from .models import *
from .serializers import *


def transaction_details_by_booking_id(booking_id):
    try:
        transactions = TransactionDetails.objects.get(booking_id=booking_id)
        return TransactionSerializer(transactions).data
    except:
        return {}


def new_transaction(trasaction_data):
    valid_serializer = TransactionDetailsSerializer(data=trasaction_data)
    if valid_serializer.is_valid():
        serializer = TransactionDetailsSerializer()
        serializer.create(trasaction_data)
        return {"status":True,"errors":""}
    else:
        return {"status":False,"errors":valid_serializer.errors}