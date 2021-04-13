from rest_framework import serializers


class ProductBookingSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=16)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class ProductAvailabilitySerializer(ProductBookingSerializer):
    product_quantity = serializers.IntegerField()


class RentBookingSerializer(ProductBookingSerializer):
    booking_id = serializers.CharField(max_length=16)
    is_cancelled = serializers.BooleanField(allow_null=True)


class RentBookingWithQuantitySerializer(RentBookingSerializer):
    product_quantity = serializers.IntegerField()


class RentBookingIdSerializer(serializers.Serializer):
    booking_id = serializers.CharField(max_length=16)
    product_id = serializers.CharField(max_length=16)

