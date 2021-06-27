from rest_framework import serializers
from .models import *


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProducts
        fields = '__all__'

    def bulk_create(self, validated_data):
        new_products = []
        for product in validated_data:
            add_booking_product = CartProducts(
                cart=product["cart"],
                product_id=product["product_id"],
                quantity=product["quantity"],
                size=product["size"],
                is_combo=product["is_combo"],
                hidden=product["hidden"],
                parent_cart_product = product["parent_cart_product"]
            )
            new_products.append(add_booking_product)
        return CartProducts.objects.bulk_create(new_products)

    def bulk_update(self, validated_data):
        cart_products = []
        for each_cart_product in validated_data:
            update_cart_product_quantity = CartProducts(
                id=each_cart_product['id'],
                quantity=each_cart_product['quantity'],
                size=each_cart_product['size']
            )
            cart_products.append(update_cart_product_quantity)
        return CartProducts.objects.bulk_update(cart_products, ['quantity', 'size'])


class TransportDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportDetails
        fields = '__all__'


class AddressSerializer(serializers.Serializer):
    name= serializers.CharField(allow_null=True)
    phone_number = serializers.CharField(max_length=10, allow_null=True)
    pincode = serializers.CharField(max_length=6, min_length=6, required=True)
    address_line = serializers.CharField(allow_null=True)
    extend_address = serializers.CharField(allow_null=True)
    landmark = serializers.CharField(allow_null=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    latitude = serializers.CharField(allow_null=True)
    longitude = serializers.CharField(allow_null=True)


class AddtoCartTransportDetailsSerializer(serializers.Serializer):
    trip_type = serializers.CharField(required=True)
    pickup_location = AddressSerializer()
    drop_location = AddressSerializer()
    km_limit_choosen = serializers.IntegerField(required=True)


class AddProductToCartSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    quantity = serializers.IntegerField(required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    # TODO: add validation for transport details and other inputs for add to cart
    transport_details = AddtoCartTransportDetailsSerializer(allow_null=True)
    #, allow_blank=True) - getting error while passing it  --__init__() got an unexpected keyword argument 'allow_blank'


class CheckoutCartSerializer(serializers.Serializer):
    entity_type = serializers.CharField(required=True)
