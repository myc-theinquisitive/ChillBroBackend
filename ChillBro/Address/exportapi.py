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


def get_latitude_longitude(address_id):
    from .models import Address
    try:
        address = Address.objects.get(id=address_id)
        return {'is_valid': True, 'latitude': address.latitude, 'longitude': address.longitude}
    except ObjectDoesNotExist:
        return {"is_valid": False, "address_id": None, "errors": "Invalid Address Id"}

def get_multiple_latitude_longitude(address_ids):
    from .models import Address
    addresses = Address.objects.filter(id__in=address_ids)
    return addresses