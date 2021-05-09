from Address.exportapi import create_address


def post_create_address(city,pincode):
    return create_address({'city':city, 'pincode':pincode})


def get_total_products_count_in_entities(entity_ids):
    from Product.exportapi import total_products_count_in_entities
    return total_products_count_in_entities(entity_ids)

  
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
