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
        print("validated_date", validated_data)
        cart_products = []
        for each_cart_product in validated_data:
            update_cart_product_quantity = CartProducts(
                id=each_cart_product['id'],
                cart = each_cart_product['cart'],
                quantity=each_cart_product['quantity'],
                size=each_cart_product['size']
            )
            cart_products.append(update_cart_product_quantity)
        return CartProducts.objects.bulk_update(cart_products, ['cart','quantity', 'size'])


class TransportDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportDetails
        fields = '__all__'


class AddtoCartTransportDetailsSerializer(serializers.Serializer):
    trip_type = serializers.CharField(required=True)
    is_pickup_location_updated = serializers.BooleanField(required=True)
    id_drop_location_updated = serializers.BooleanField(required=True)
    km_limit_choosen = serializers.IntegerField(required=True)


class AddProductToCartSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    quantity = serializers.IntegerField(required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    # TODO: add validation for transport details and other inputs for add to cart
    # transport_details = AddtoCartTransportDetailsSerializer(allow_null=True)


class CheckoutCartSerializer(serializers.Serializer):
    entity_type = serializers.CharField(required=True)
