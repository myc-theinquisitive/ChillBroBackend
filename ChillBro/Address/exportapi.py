from .serializers import AddressSerializer


def create_address(address_details):
    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        serializer = valid_serializer.save()
        return {"is_valid": True,"address_id":serializer.data,"errors":None}
    else:
        return {"is_valid": False,"address_id":None, "errors":valid_serializer.errors}

