from .wrapper import *
from collections import defaultdict


def is_product_valid(product_details, product_id, quantity, all_sizes, combo_product_details):
    """
        product_details :(dict of dict)
            "c27d280f-339e-4444-865b-25f1dde85db8": {
            "product_id": "c27d280f-339e-4444-865b-25f1dde85db8",
            "price": 1000.0,
            "price_by_type": 1900.0,
            "price_type": "DAY",
            "net_value_details": {
                "net_price": 680.0,
                "details": {
                    "final_selling_price": 1000.0,
                    "commission_fee": 100.0,
                    "transaction_fee": 20.0,
                    "fixed_fee": 20.0,
                    "gst": 180.0
                }
            },
            "discount": 47.36842105263158,
            "quantity_unlimited": false,
            "quantity": 10,
            "name": "Rockzz Event",
            "type": "EVENT",
            "has_sizes": false,
            "is_combo": false,
            "has_sub_products": false,
            "size_products": {},
            "combo_products": {},
            "sub_products": {},
            "transport_details": {},
            "event_details": {
                "id": 1,
                "product": "c27d280f-339e-4444-865b-25f1dde85db8",
                "tags": [
                    "DJ",
                    "Private Party"
                ],
                "mode": "ONLINE",
                "host_app": "ZOOM",
                "url_link": "url yet to be added",
                "payment_type": "FREE",
                "has_slots": true,
                "start_time": "2021-11-25T00:00:00+05:30",
                "end_time": "2021-11-27T00:00:00+05:30",
                "slots": [
                    {
                        "id": 1,
                        "name": "Morning",
                        "day_start_time": "08:00:00",
                        "day_end_time": "12:00:00"
                    },
                    {
                        "id": 2,
                        "name": "Afternoon",
                        "day_start_time": "13:00:00",
                        "day_end_time": "16:00:00"
                    },
                    {
                        "id": 3,
                        "name": "Evening",
                        "day_start_time": "17:00:00",
                        "day_end_time": "20:00:00"
                    }
                ],
                "price_classes": [
                    {
                        "id": 1,
                        "name": "LUXARY",
                        "price": 1200.0
                    },
                    {
                        "id": 2,
                        "name": "SUPER LUXARY",
                        "price": 1500.0
                    },
                    {
                        "id": 3,
                        "name": "NORMAL",
                        "price": 1000.0
                    }
                ]
            }
        }
    """
    is_valid = True
    errors = defaultdict(list)
    if quantity < 1:
        is_valid = False
        errors[product_id].append("Quantity must be greater than zero")

    if product_details[product_id]['has_sizes']:
        product_sizes_details = product_details[product_id]['size_products']
        if len(all_sizes) == 0 and len(product_sizes_details) > 0:
            is_valid = False
            errors[product_id].append("Please choose sizes")
        else:
            total_quantity = 0
            for each_size in all_sizes:
                try:
                    # for validation of size - if the size selected by user is valid for this product or not
                    products_quantity = product_sizes_details[each_size]
                    total_quantity += all_sizes[each_size]
                except KeyError:
                    is_valid = False
                    errors[product_id].append("Invalid Size")
            if total_quantity != quantity:
                is_valid = False
                errors[product_id].append("Please select sizes for all quantity - {}".format(quantity))

    if product_details[product_id]["is_combo"]:
        combo_products_data = product_details[product_id]['combo_products']
        if len(combo_products_data) != len(combo_product_details):
            is_valid = False
            errors[product_id].append("Invalid combo product data")

        # combo sub products sizes will be checked in booking validation
        # TODO: Better to validate sizes here as well  --- booking validation means checking in adding cart only sir
        for each_combo_product in combo_product_details:
            try:
                product_quantity = combo_products_data[each_combo_product]['quantity']
                combo_product_size_details = combo_product_details[each_combo_product]
                total_product_quantity = 0
                for each_size in combo_product_size_details:
                    total_product_quantity += combo_product_size_details[each_size]

                if len(combo_product_size_details) > 0 and \
                        product_quantity * quantity != total_product_quantity:
                    is_valid = False
                    errors[product_id].append("{} product should have {} sizes"
                                              .format(each_combo_product, product_quantity * quantity))
            except KeyError:
                is_valid = False
                errors[product_id].append("Invalid combo product data")

    return is_valid, errors
