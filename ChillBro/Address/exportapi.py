from .serializers import AddressSerializer


def create_address(address_details):
    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        address_create = AddressSerializer()
        address = address_create.create(address_details)
        return address.id
    else:
        return valid_serializer.errors

