from .Category.serializers import *
from .BaseProduct.serializers import *
from .BaseProduct.constants import ProductTypes


class IdsListSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField()
    )
