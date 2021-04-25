from rest_framework import serializers
from .models import *


class TransactionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetails
        fields = '__all__'


class TransactionSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=True)
    utr = serializers.CharField(required=True)
    mode = serializers.CharField(required=True)
    transaction_date = serializers.DateTimeField(required=True)


class CustomDatesSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(required=True)
    to_date = serializers.DateTimeField(required=True)


class PaymentRevenueStatisticsViewSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_filters = serializers.ListField(
        child=serializers.CharField()
    )
    entity_ids = serializers.ListField(
        child=serializers.CharField(required=True, min_length=36, max_length=36)
    )
    custom_dates = CustomDatesSerializer(required=False)