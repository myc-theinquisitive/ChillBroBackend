from Address.exportapi import *


def post_create_address(city,pincode):
    return create_address({'city':city, 'pincode':pincode})