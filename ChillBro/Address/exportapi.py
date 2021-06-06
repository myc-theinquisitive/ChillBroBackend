from django.core.exceptions import ObjectDoesNotExist
from .serializers import AddressSerializer
from .views import address_details_for_address_ids


def create_address(address_details):
    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        serializer = valid_serializer.create(address_details)
        return {"is_valid": True, "address_id": serializer.id, "errors": None}
    else:
        return {"is_valid": False, "address_id": None, "errors": valid_serializer.errors}


def get_address_details(address_ids):
    return address_details_for_address_ids(address_ids)


def update_address(address_id, address_details):
    from .models import Address
    try:
        address = Address.objects.get(id=address_id)
    except ObjectDoesNotExist:
        return {"is_valid": False, "address_id": None, "errors": "Invalid Address Id"}

    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        serializer = valid_serializer.update(address, address_details)
        return {"is_valid": True, "address_id": serializer.id, "errors": None}
    else:
        return {"is_valid": False, "address_id": None, "errors": valid_serializer.errors}


def filter_by_city(address_ids, city):
    from .models import Address
    return Address.objects.filter(id__in=address_ids).filter(city=city).values_list("id", flat=True)
