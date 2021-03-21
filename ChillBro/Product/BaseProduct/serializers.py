from rest_framework import serializers
from .models import Product, ProductImage
from ..Category.serializers import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        lookup_field = 'slug'
        fields = '__all__'

    def create(self, validated_data):
        if "featured" not in validated_data:
            validated_data["featured"] = False
        if "active" not in validated_data:
            validated_data["active"] = True

        return Product.objects.create(
            name=validated_data["name"], description=validated_data["description"],
            type=validated_data["type"], category_id=validated_data["category"], price=validated_data["price"],
            discounted_price=validated_data["discounted_price"], featured=validated_data["featured"],
            active=validated_data["active"])

    def update(self, instance, validated_data):
        if "featured" not in validated_data:
            validated_data["featured"] = False
        if "active" not in validated_data:
            validated_data["active"] = True

        instance.name = validated_data["name"]
        instance.description = validated_data["description"]
        instance.type = validated_data["type"]
        instance.category_id = validated_data["category"]
        instance.price = validated_data["price"]
        instance.discounted_price = validated_data["discounted_price"]
        instance.featured = validated_data["featured"]
        instance.save()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
