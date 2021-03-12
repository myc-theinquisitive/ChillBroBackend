from rest_framework import serializers
from .helpers import get_coupon_code_length


class UseCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=get_coupon_code_length())
    entity_id = serializers.CharField(max_length=16)
    order_id = serializers.CharField(max_length=16)
    order_value = serializers.IntegerField()


class DiscountSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=get_coupon_code_length())
    entity_id = serializers.CharField(max_length=16)
    order_value = serializers.IntegerField()
