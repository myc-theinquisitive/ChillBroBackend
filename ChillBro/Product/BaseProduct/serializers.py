from rest_framework import serializers
from .models import Product, ProductImage


class ProductSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField('get_features')

    @staticmethod
    def get_features(instance):
        return []

    class Meta:
        model = Product
        lookup_field = 'slug'
        fields = '__all__'

    def create(self, validated_data):
        if "featured" not in validated_data:
            validated_data["featured"] = False
        if "active" not in validated_data:
            validated_data["active"] = True

        product = Product.objects.create(
            name=validated_data["name"], description=validated_data["description"],
            type=validated_data["type"], category=validated_data["category"], price=validated_data["price"],
            discounted_price=validated_data["discounted_price"], featured=validated_data["featured"],
            active=validated_data["active"], quantity= validated_data["quantity"])

        if "tags" in validated_data:
            product.tags.add(*validated_data["tags"])
        if "features" in validated_data:
            product.kvstore.set(validated_data["features"])
        return product

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
        instance.quantity = validated_data["quantity"]

        if "tags" in validated_data:
            instance.tags.set(*validated_data["tags"])
        if "features" in validated_data:
            if "add" in validated_data["features"]:
                instance.kvstore.set(validated_data["features"]["add"])
            if "delete" in validated_data["features"]:
                for key in validated_data["features"]["delete"]:
                    instance.kvstore.delete(key)
        instance.save()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['quantity']
