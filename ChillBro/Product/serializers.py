from .Category.serializers import *
from .BaseProduct.serializers import *
from .BaseProduct.constants import ProductTypes
from .Seller.serializers import *


class IdsListSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField()
    )
