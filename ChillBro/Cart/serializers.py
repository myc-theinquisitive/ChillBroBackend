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
        return CartProducts.objects.bulk_update(cart_products,['quantity','size'])


class CartProductExtraDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProductExtraDetails
        fields = '__all__'


class AddProductToCartSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    quantity = serializers.IntegerField(required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)


class CheckoutCartSerializer(serializers.Serializer):
    entity_type = serializers.CharField(required=True)
