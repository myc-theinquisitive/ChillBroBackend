from .Category.serializers import *
from .BaseProduct.serializers import *
from .BaseProduct.constants import ProductTypes
from .Seller.serializers import *


class IdsListSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField()
    )


class NetPriceSerializer(serializers.Serializer):
    selling_price = serializers.IntegerField()
    discount = serializers.IntegerField(max_value=100)


class PriceFilter(serializers.Serializer):
    applied = serializers.BooleanField(default=False)
    min_amount = serializers.DecimalField(decimal_places=2, max_digits=20, allow_null=True)
    max_amount = serializers.DecimalField(decimal_places=2, max_digits=20, allow_null=True)


class LocationFilter(serializers.Serializer):
    applied = serializers.BooleanField(default=False)
    city = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)


class GetProductsBySearchFilters(serializers.Serializer):
    search_text = serializers.CharField(allow_null=True, allow_blank=True)
    sort_filter = serializers.CharField(allow_null=True, allow_blank=True)
    price_filter = PriceFilter()
    location_filter = LocationFilter()


class GetBusinessClientProductsByStatusSerializer(serializers.Serializer):
    seller_ids = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )
    statuses = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )
