from .serializers import AddressSerializer


def submit_address_data(city, pincode):
    address_create = AddressSerializer()
    address = address_create.create({'city':city, 'pincode':pincode})
    return address.id

