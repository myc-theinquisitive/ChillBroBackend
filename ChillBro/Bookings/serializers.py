from rest_framework import serializers
from .models import *


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'


class OrderedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedProducts
        fields = '__all__'
    def bulk_create(self, validated_data):
        # print(validated_data)
        # for i in validated_data:
        #     print(i)
        #     super().create(i)
        all_products = []
        for product in validated_data:
            update_amenity = OrderedProducts(
                booking_id=product["booking_id"],
                product_id=product["product_id"],
                entity=product["entity"],
                start_time = product["start_time"],
                end_time = product["end_time"],
                product_value = product["product_value"],
                quantity = product["quantity"]
            )
            all_products.append(update_amenity)
        OrderedProducts.objects.bulk_create(all_products)
        return True


