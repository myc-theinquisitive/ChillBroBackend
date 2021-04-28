from Address.exportapi import *


def post_address_data(city,pincode):
    address_id = submit_address_data(city,pincode)
    return address_id