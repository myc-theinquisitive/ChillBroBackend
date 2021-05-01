from Address.exportapi import *


def post_create_address(city,pincode):
    address_id = create_address({'city':city, 'pincode':pincode})
    return address_id