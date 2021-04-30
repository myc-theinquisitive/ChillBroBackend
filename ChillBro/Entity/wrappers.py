def post_address_data(city, pincode):
    # address_id = submit_address_data(city,pincode)
    address_id = "dfe4-34dj-5683kd-3829"
    return address_id


def get_address_details_for_address_ids(address_ids):
    addresses = []
    for address_id in address_ids:
        address = {
            "id": address_id,
            "pincode": "555555",
            "city": "VISAKHAPATANAM"
        }
        addresses.append(address)
    return addresses
