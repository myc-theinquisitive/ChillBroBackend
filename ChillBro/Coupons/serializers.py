from rest_framework import serializers
from .helpers import get_coupon_code_length
from .models import Discount, AllowedUsersRule, AllowedEntitiesRule, AllowedProductsRule, ValidityRule, \
    MaxUsesRule, Ruleset, Coupon, CouponHistory, AllowedProductTypesRule


class CouponCodeSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=get_coupon_code_length)


class AvailableCouponSerializer(serializers.Serializer):
    entity_ids = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )
    product_ids = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )
    product_types = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )
    order_value = serializers.IntegerField()


class GetDiscountSerializer(AvailableCouponSerializer):
    coupon_code = serializers.CharField(max_length=get_coupon_code_length)


class UseCouponSerializer(GetDiscountSerializer):
    order_id = serializers.CharField(max_length=36)


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class AllowedUsersSerializer(serializers.ModelSerializer):
    users = serializers.JSONField()

    class Meta:
        model = AllowedUsersRule
        fields = '__all__'


class AllowedEntitiesSerializer(serializers.ModelSerializer):
    entities = serializers.JSONField()

    class Meta:
        model = AllowedEntitiesRule
        fields = '__all__'


class AllowedProductsSerializer(serializers.ModelSerializer):
    products = serializers.JSONField()

    class Meta:
        model = AllowedProductsRule
        fields = '__all__'


class AllowedProductTypesSerializer(serializers.ModelSerializer):
    product_types = serializers.JSONField()

    class Meta:
        model = AllowedProductTypesRule
        fields = '__all__'


class ValidityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidityRule
        fields = '__all__'


class MaxUsesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaxUsesRule
        fields = '__all__'


class RuleSetSerializer(serializers.ModelSerializer):
    allowed_users = AllowedUsersSerializer()
    allowed_entities = AllowedEntitiesSerializer()
    allowed_products = AllowedProductsSerializer()
    allowed_product_types = AllowedProductTypesSerializer()
    max_uses = MaxUsesSerializer()
    validity = ValidityRuleSerializer()

    class Meta:
        model = Ruleset
        fields = '__all__'

    def create(self, validated_data):
        allowed_users = validated_data.pop('allowed_users', None)
        allowed_users_serializer = AllowedUsersSerializer(data=allowed_users)
        allowed_users_serializer.is_valid(raise_exception=True)
        allowed_users_obj = allowed_users_serializer.save()
        validated_data["allowed_users"] = allowed_users_obj

        allowed_entities = validated_data.pop('allowed_entities', None)
        allowed_entities_serializer = AllowedEntitiesSerializer(data=allowed_entities)
        allowed_entities_serializer.is_valid(raise_exception=True)
        allowed_entities_obj = allowed_entities_serializer.save()
        validated_data["allowed_entities"] = allowed_entities_obj

        allowed_products = validated_data.pop('allowed_products', None)
        allowed_products_serializer = AllowedProductsSerializer(data=allowed_products)
        allowed_products_serializer.is_valid(raise_exception=True)
        allowed_products_obj = allowed_products_serializer.save()
        validated_data["allowed_products"] = allowed_products_obj

        allowed_product_types = validated_data.pop('allowed_product_types', None)
        allowed_product_types_serializer = AllowedProductTypesSerializer(data=allowed_product_types)
        allowed_product_types_serializer.is_valid(raise_exception=True)
        allowed_product_types_obj = allowed_product_types_serializer.save()
        validated_data["allowed_product_types"] = allowed_product_types_obj

        max_uses = validated_data.pop('max_uses', None)
        max_uses_serializer = MaxUsesSerializer(data=max_uses)
        max_uses_serializer.is_valid(raise_exception=True)
        max_uses_obj = max_uses_serializer.save()
        validated_data["max_uses"] = max_uses_obj

        validity = validated_data.pop('validity', None)
        validity_serializer = ValidityRuleSerializer(data=validity)
        validity_serializer.is_valid(raise_exception=True)
        validity_obj = validity_serializer.save()
        validated_data["validity"] = validity_obj

        return super().create(validated_data)

    def update(self, instance, validated_data):
        allowed_users = validated_data.pop('allowed_users', None)
        allowed_users_serializer = AllowedUsersSerializer(data=allowed_users)
        allowed_users_serializer.is_valid(raise_exception=True)
        allowed_users_obj = allowed_users_serializer.update(instance.allowed_users, allowed_users)
        validated_data["allowed_users"] = allowed_users_obj

        allowed_entities = validated_data.pop('allowed_entities', None)
        allowed_entities_serializer = AllowedEntitiesSerializer(data=allowed_entities)
        allowed_entities_serializer.is_valid(raise_exception=True)
        allowed_entities_obj = allowed_entities_serializer.update(instance.allowed_entities, allowed_entities)
        validated_data["allowed_entities"] = allowed_entities_obj

        allowed_products = validated_data.pop('allowed_products', None)
        allowed_products_serializer = AllowedProductsSerializer(data=allowed_products)
        allowed_products_serializer.is_valid(raise_exception=True)
        allowed_products_obj = allowed_products_serializer.update(instance.allowed_products, allowed_products)
        validated_data["allowed_products"] = allowed_products_obj

        allowed_product_types = validated_data.pop('allowed_product_types', None)
        allowed_product_types_serializer = AllowedProductTypesSerializer(data=allowed_product_types)
        allowed_product_types_serializer.is_valid(raise_exception=True)
        allowed_product_types_obj = allowed_product_types_serializer.update(
            instance.allowed_product_types, allowed_product_types)
        validated_data["allowed_product_types"] = allowed_product_types_obj

        max_uses = validated_data.pop('max_uses', None)
        max_uses_serializer = MaxUsesSerializer(data=max_uses)
        max_uses_serializer.is_valid(raise_exception=True)
        max_uses_obj = max_uses_serializer.update(instance.max_uses, max_uses)
        validated_data["max_uses"] = max_uses_obj

        validity = validated_data.pop('validity', None)
        validity_serializer = ValidityRuleSerializer(data=validity)
        validity_serializer.is_valid(raise_exception=True)
        validity_obj = validity_serializer.update(instance.validity, validity)
        validated_data["validity"] = validity_obj

        return super().update(instance, validated_data)


class CouponSerializer(serializers.ModelSerializer):
    discount = DiscountSerializer()
    ruleset = RuleSetSerializer()
    terms_and_conditions = serializers.JSONField()

    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('times_used', 'created')

    def store_history(self, coupon):
        request_user = self.context['request'].user

        discount = coupon.discount
        discount.pk = None
        discount.save()

        ruleset = coupon.ruleset

        allowed_users = ruleset.allowed_users
        allowed_users.pk = None
        allowed_users.save()

        allowed_entities = ruleset.allowed_entities
        allowed_entities.pk = None
        allowed_entities.save()

        allowed_products = ruleset.allowed_products
        allowed_products.pk = None
        allowed_products.save()

        allowed_product_types = ruleset.allowed_product_types
        allowed_product_types.pk = None
        allowed_product_types.save()

        max_uses = ruleset.max_uses
        max_uses.pk = None
        max_uses.save()

        validity = ruleset.validity
        validity.pk = None
        validity.save()

        ruleset.pk = None
        ruleset.allowed_users = allowed_users
        ruleset.allowed_entities = allowed_entities
        ruleset.allowed_products = allowed_products
        ruleset.allowed_product_types = allowed_product_types
        ruleset.max_uses = max_uses
        ruleset.validity = validity
        ruleset.save()

        CouponHistory.objects.create(code=coupon.code, discount=discount, times_used=coupon.times_used,
                                     ruleset=ruleset, changed_by=request_user)

    def create(self, validated_data):
        discount = validated_data.pop('discount', None)
        discount_serializer = DiscountSerializer(data=discount)
        discount_serializer.is_valid(raise_exception=True)
        discount_obj = discount_serializer.save()
        validated_data["discount"] = discount_obj

        ruleset = validated_data.pop('ruleset', None)
        ruleset_serializer = RuleSetSerializer(data=ruleset)
        ruleset_serializer.is_valid(raise_exception=True)
        ruleset_obj = ruleset_serializer.save()
        validated_data["ruleset"] = ruleset_obj

        coupon = super().create(validated_data)
        self.store_history(coupon)
        return coupon

    def update(self, instance, validated_data):

        discount = validated_data.pop('discount', None)
        discount_serializer = DiscountSerializer(data=discount)
        discount_serializer.is_valid(raise_exception=True)
        discount_obj = discount_serializer.update(instance.discount, discount)
        validated_data["discount"] = discount_obj

        ruleset = validated_data.pop('ruleset', None)
        ruleset_serializer = RuleSetSerializer(data=ruleset)
        ruleset_serializer.is_valid(raise_exception=True)
        ruleset_obj = ruleset_serializer.update(instance.ruleset, ruleset)
        validated_data["ruleset"] = ruleset_obj

        coupon = super().update(instance, validated_data)
        self.store_history(coupon)
        return coupon


class CouponHistorySerializer(serializers.ModelSerializer):
    discount = DiscountSerializer()
    ruleset = RuleSetSerializer()

    class Meta:
        model = CouponHistory
        fields = '__all__'
        read_only_fields = ('times_used', 'created', 'changed_by')
