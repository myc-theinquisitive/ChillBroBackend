from rest_framework import serializers
from .models import Product, ProductImage, ProductVerification


class ProductSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField('get_features')

    @staticmethod
    def get_features(instance):
        return []

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('active_from', 'activation_status', )

    def create(self, validated_data):
        if "featured" not in validated_data:
            validated_data["featured"] = False
        if "quantity" not in validated_data:
            validated_data["quantity"] = 0

        product = Product.objects.create(
            name=validated_data["name"], description=validated_data["description"],
            type=validated_data["type"], category_id=validated_data["category"], price=validated_data["price"],
            discounted_price=validated_data["discounted_price"], featured=validated_data["featured"],
            quantity=validated_data["quantity"])

        if "tags" in validated_data:
            product.tags.add(*validated_data["tags"])
        if "features" in validated_data:
            product.kvstore.set(validated_data["features"])
        return product

    def update(self, instance, validated_data):
        if "featured" not in validated_data:
            validated_data["featured"] = False
        if "quantity" not in validated_data:
            validated_data["quantity"] = 0

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

    @staticmethod
    def bulk_create(product_images):
        all_images = []
        for image in product_images:
            each_image = ProductImage(
                product=image['product'],
                image=image['image']
            )
            all_images.append(each_image)
        ProductImage.objects.bulk_create(all_images)


class ProductQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['quantity']


class ProductVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVerification
        fields = '__all__'


class ProductVerificationUpdateInputSerializer(serializers.ModelSerializer):
    comments = serializers.CharField()

    class Meta:
        model = Product
        fields = ('activation_status', 'comments', )
