from rest_framework import serializers
from .models import *


class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'


class BookedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedProducts
        fields = '__all__'

    def bulk_create(self, validated_data):
        new_products = []
        for product in validated_data:
            add_booking_product = BookedProducts(
                booking_id=product["booking_id"],
                product_id=product["product_id"],
                entity_id=product["entity_id"],
                start_time=product["start_time"],
                end_time=product["end_time"],
                product_value=product["product_value"],
                quantity=product["quantity"]
            )
            new_products.append(add_booking_product)
        return BookedProducts.objects.bulk_create(new_products)


class BookingIdSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)


class NewProductSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True,min_length=36, max_length=36)
    entity_id = serializers.CharField(required=True,min_length=36, max_length=36)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    quantity = serializers.IntegerField(required=True)


class NewBookingSerializer(serializers.Serializer):
    coupon = serializers.CharField(required=True,min_length=36, max_length=36)
    products = NewProductSerializer(many=True)
    entity_type = serializers.CharField(required=True)
    payment_status = serializers.CharField(required=True)


class StatisticsSerializer(serializers.Serializer):
    booking_filter = serializers.CharField(required=True)
    entity_type = serializers.CharField(required=False)

class OrderDetailsSerializer(serializers.Serializer):
    booking_filter = serializers.CharField(required=True)
    entity_type = serializers.CharField(required=False)
    status = serializers.ListField(
        child=serializers.CharField()
    )

