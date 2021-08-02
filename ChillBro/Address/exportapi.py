from .serializers import AddressSerializer
from .helpers import create_address, get_address_details, update_address


def filter_by_city(address_ids, city):
    from .models import Address
    return Address.objects.filter(id__in=address_ids).filter(city=city).values_list("id", flat=True)


def validate_address(address_details):
    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        return True, {}
    else:
        return False, valid_serializer.errors
