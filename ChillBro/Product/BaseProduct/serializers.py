from rest_framework import serializers
from .models import Product, ProductImage, ProductVerification, ComboProductItems, ProductSize
from .constants import PriceTypes


class ProductSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField('get_features')

    @staticmethod
    def get_features(instance):
        return []

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('active_from', 'activation_status', )

    @staticmethod
    def add_default_values(validated_data):
        if "featured" not in validated_data:
            validated_data["featured"] = False
        if "quantity" not in validated_data:
            validated_data["quantity"] = 0
        if "is_combo" not in validated_data:
            validated_data["is_combo"] = False
        if "has_sizes" not in validated_data:
            validated_data["has_sizes"] = False
        if "price_type" not in validated_data:
            validated_data["price_type"] = PriceTypes.DAY.value

    def create(self, validated_data):
        self.add_default_values(validated_data)

        product = Product.objects.create(
            name=validated_data["name"], description=validated_data["description"],
            type=validated_data["type"], category_id=validated_data["category"], price=validated_data["price"],
            discounted_price=validated_data["discounted_price"], featured=validated_data["featured"],
            quantity=validated_data["quantity"], is_combo=validated_data["is_combo"],
            has_sizes=validated_data["has_sizes"], price_type=validated_data["price_type"])

        if "tags" in validated_data:
            product.tags.add(*validated_data["tags"])
        if "features" in validated_data:
            product.kvstore.set(validated_data["features"])

        # Adding items for combo product
        if validated_data["is_combo"]:
            combo_items = []
            for combo_item in validated_data["combo_items"]:
                combo_item_dict = {
                    "product": product.id,
                    "combo_item": combo_item["product_id"],
                    "quantity": combo_item["quantity"]
                }
                combo_items.append(combo_item_dict)
            ComboProductItemsSerializer.bulk_create(combo_items)

        # Adding sizes for product
        if validated_data["has_sizes"]:
            sizes = []
            for product_size in validated_data["sizes"]:
                product_size_dict = {
                    "product": product.id,
                    "size": product_size["size"],
                    "quantity": product_size["quantity"],
                    "order": product_size["order"]
                }
                sizes.append(product_size_dict)
            ProductSizeSerializer.bulk_create(sizes)

        return product

    def update(self, instance, validated_data):
        self.add_default_values(validated_data)

        instance.name = validated_data["name"]
        instance.description = validated_data["description"]
        instance.type = validated_data["type"]
        instance.category_id = validated_data["category"]
        instance.price = validated_data["price"]
        instance.discounted_price = validated_data["discounted_price"]
        instance.featured = validated_data["featured"]
        instance.quantity = validated_data["quantity"]
        instance.is_combo = validated_data["is_combo"]
        instance.has_sizes = validated_data["has_sizes"]
        instance.price_type = validated_data["price_type"]

        if "tags" in validated_data:
            instance.tags.set(*validated_data["tags"])
        if "features" in validated_data:
            if "add" in validated_data["features"]:
                instance.kvstore.set(validated_data["features"]["add"])
            if "delete" in validated_data["features"]:
                for key in validated_data["features"]["delete"]:
                    instance.kvstore.delete(key)

        if validated_data["is_combo"]:

            # Adding items for combo product
            add_combo_items = []
            for combo_item in validated_data["combo_items"]["add"]:
                combo_item_dict = {
                    "product": instance.id,
                    "combo_item": combo_item["product_id"],
                    "quantity": combo_item["quantity"]
                }
                add_combo_items.append(combo_item_dict)
            ComboProductItemsSerializer.bulk_create(add_combo_items)

            # Deleting items for combo product
            delete_combo_items = validated_data["combo_items"]["delete"]
            ComboProductItemsSerializer.bulk_delete(instance.id, delete_combo_items)

        if validated_data["has_sizes"]:

            # Adding sizes for product
            add_sizes = []
            for product_size in validated_data["sizes"]["add"]:
                product_size_dict = {
                    "product": instance.id,
                    "size": product_size["size"],
                    "quantity": product_size["quantity"],
                    "order": product_size["order"]
                }
                add_sizes.append(product_size_dict)
            ProductSizeSerializer.bulk_create(add_sizes)

            # Deleting sizes for product
            delete_sizes = validated_data["sizes"]["delete"]
            ProductSizeSerializer.bulk_delete(instance.id, delete_sizes)

        instance.save()


class ProductSizeSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = ProductSize
        fields = '__all__'

    @staticmethod
    def bulk_create(product_sizes):
        all_sizes = []
        for product_size in product_sizes:
            product_size_obj = ProductSize(
                product_id=product_size['product'],
                size=product_size['size'],
                quantity=product_size['quantity'],
                order=product_size['order']
            )
            all_sizes.append(product_size_obj)
        ProductSize.objects.bulk_create(all_sizes)

    @staticmethod
    def bulk_delete(product_id, product_sizes):
        ProductSize.objects.filter(product_id=product_id, size__in=product_sizes).delete()


class ComboProductItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComboProductItems
        fields = '__all__'

    @staticmethod
    def bulk_create(combo_products):
        all_products = []
        for combo_product in combo_products:
            combo_product_obj = ComboProductItems(
                product_id=combo_product['product'],
                combo_item_id=combo_product['combo_item'],
                quantity=combo_product["quantity"]
            )
            all_products.append(combo_product_obj)
        ComboProductItems.objects.bulk_create(all_products)

    @staticmethod
    def bulk_delete(product_id, combo_product_ids):
        ComboProductItems.objects.filter(product_id=product_id, combo_item__in=combo_product_ids).delete()


class ProductImageSerializer(serializers.Serializer):

    product = serializers.CharField(max_length=36)
    image = serializers.ImageField()
    order = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return ProductImage.objects.create(product_id=validated_data["product"],
                                           image=validated_data["image"], order=validated_data["order"])

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


class ProductQuantityUpdateSerializer(serializers.Serializer):
    size = serializers.CharField(max_length=10, allow_null=True, allow_blank=True)
    quantity = serializers.IntegerField()


class ProductVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVerification
        fields = '__all__'


class ProductVerificationUpdateInputSerializer(serializers.ModelSerializer):
    comments = serializers.CharField()

    class Meta:
        model = Product
        fields = ('activation_status', 'comments', )
