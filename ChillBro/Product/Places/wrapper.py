from Address.exportapi import create_address, update_address, get_address_details


def post_create_address(address_data):
    return create_address(address_data)


def update_address_for_address_id(address_id, address_data):
    return update_address(address_id, address_data)


def get_address_details_for_address_ids(address_ids):
    return get_address_details(address_ids)
