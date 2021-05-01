from rest_framework import serializers
from .models import *


class BookingTransactionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTransaction
        fields = '__all__'


class UpdateBookingTransactionSerializer(serializers.Serializer):
    booking_ids = serializers.ListField(
        child=serializers.CharField(max_length=36, required=True)
    ),
    transaction_id = serializers.CharField(max_length=36, required=True)
    utr = serializers.CharField(max_length=30, required=True)
    mode = serializers.CharField(max_length=30, required=True)
    transaction_date = serializers.DateTimeField(required=True)


class CODBookingTransactionSerializer(serializers.Serializer):
    booking_id = serializers.CharField(max_length=36, required=True)
    transaction_id = serializers.CharField(max_length=36, required=True)
    utr = serializers.CharField(max_length=30, required=True)
    mode = serializers.CharField(max_length=30, required=True)
    transaction_date = serializers.DateTimeField(required=True)


class CustomDatesSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(required=True)
    to_date = serializers.DateTimeField(required=True)


class PaymentRevenueStatisticsViewSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_filters = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )
    entity_ids = serializers.ListField(
        child=serializers.CharField(required=True, min_length=36, max_length=36)
    )
    custom_dates = CustomDatesSerializer(required=False)


class PaymentStatasticsDetailsInputSerializer(PaymentRevenueStatisticsViewSerializer):
    statistics_details_type = serializers.CharField(max_length=50)
