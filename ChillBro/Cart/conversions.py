from collections import defaultdict
from .wrapper import *


def convert_combo_products_list_to_dict_of_dictionaries(list_of_combo_products):
    """
        list_of_combo_products: (list of dict)
            [
                {
                    "product_id":"48675d13-a700-4593-ac09-f5063ceaa386",
                    "sizes":[
                        {
                            "size":"",
                            "quantity":1
                        }
                    ]
                },
                {
                    "product_id":"af8524ad-47a7-469b-9066-294ea315f65b",
                    "sizes":[
                        {
                            "size":"L",
                            "quantity":1
                        },
                        {
                            "size":"XS",
                            "quantity":1
                        }
                    ]
                },
                {
                    "product_id":"fdf090e0-ca32-4b27-8bfe-d37d4818334e",
                    "sizes":[
                        {
                            "size":"XS",
                            "quantity":2
                        }
                    ]
                }
            ]
    """
    dict_of_combo_products = defaultdict()
    for each_combo_product in list_of_combo_products:
        dict_of_sizes = defaultdict()
        for each_size in each_combo_product['sizes']:
            dict_of_sizes[each_size['size']] = each_size['quantity']
        dict_of_combo_products[each_combo_product['product_id']] = dict_of_sizes

    return dict_of_combo_products


def convert_sizes_list_to_dict(list_of_sizes):
    """
        list_of_sizes: (list of dict)
            [
                {
                    "size":"L",
                    "quantity":1
                },
                {
                    "size":"XS",
                    "quantity":1
                }
            ]
    """
    dict_of_sizes = defaultdict()
    for each_size in list_of_sizes:
        dict_of_sizes[each_size['size']] = each_size['quantity']

    return dict_of_sizes


def convert_list_of_dict_to_dict_of_dict(list_of_dict, unique_id):
    dict_of_dict = defaultdict()
    for each_dict in list_of_dict:
        dict_of_dict[each_dict[unique_id]] = each_dict

    return dict_of_dict


def combine_products(all_cart_products):
    form_together = defaultdict()
    for each_product in all_cart_products:
        if each_product['size'] is None:
            size = ""
        else:
            size = each_product['size']
        try:
            form_together[each_product['product_id'] + "," + size] = {
                "product_id": each_product['product_id'],
                "quantity": form_together[each_product['product_id'] + "," + size]['quantity']
                            + each_product['quantity'],
                "size": each_product['size']
            }
        except KeyError:
            form_together[each_product['product_id'] + "," + size] = {
                "product_id": each_product['product_id'],
                "quantity": each_product['quantity'],
                "size": each_product['size']
            }
    final_products = []
    for each_product in form_together:
        final_products.append(form_together[each_product])

    return final_products


def combine_all_products(product_id, size, quantity, combo_product_details, product_details):
    products = []
    all_product_ids = [product_id]
    if product_details[product_id]["is_combo"]:
        combo_products_data = product_details[product_id]['combo_products']
        for each_combo_product in combo_products_data:
            all_product_ids.append(each_combo_product)
            all_sizes = combo_product_details[each_combo_product]

            if len(all_sizes) == 0:
                products.append(
                    {
                        "product_id": each_combo_product,
                        "quantity": combo_product_details[each_combo_product]['quantity'] * quantity,
                        "size": None,
                        "parent_booked_product": product_id
                    }
                )
            else:
                for each_size in all_sizes:
                    products.append(
                        {
                            "product_id": each_combo_product,
                            "quantity": all_sizes[each_size],
                            "size": each_size,
                            "parent_booked_product": product_id
                        }
                    )

    elif product_details[product_id]["has_sub_products"]:
        sub_products = product_details[product_id]["sub_products"]
        for each_sub_product in sub_products:
            all_product_ids.append(each_sub_product)
            sub_product_sizes = sub_products[each_sub_product]['size']
            if len(sub_product_sizes) == 0:
                sub_product_size = None
                products.append(
                    {
                        "product_id": each_sub_product,
                        "quantity": sub_products[each_sub_product]['quantity'] * quantity,
                        "size": sub_product_size,
                        "parent_booked_product": product_id
                    }
                )
            else:
                # this case is not there at present
                for each_size in sub_product_sizes:
                    products.append(
                        {
                            "product_id": each_sub_product,
                            "quantity": sub_product_sizes[each_size] * quantity,
                            "size": each_size,
                            "parent_booked_product": product_id
                        }
                    )
    else:
        all_sizes = size
        if len(all_sizes) == 0:
            products.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "size": None,
                    "parent_booked_product": None
                }
            )
        for each_size in all_sizes:
            products.append(
                {
                    "product_id": product_id,
                    "quantity": all_sizes[each_size],
                    "size": each_size,
                    "parent_booked_product": None
                }
            )

    return all_product_ids, products


def form_each_cart_all_products(cart_items, transport_details, event_details, product_price_values,
                                product_details, total_products_value, total_coupon_value):
    cart_products_for_bookings = defaultdict(list)
    for each_cart_product in cart_items:
        if each_cart_product.hidden:
            cart_products_for_bookings[each_cart_product.cart_id].append(
                {
                    "product_id": each_cart_product.product_id,
                    "quantity": each_cart_product.quantity,
                    "size": each_cart_product.size,
                    "parent_booked_product": each_cart_product.parent_cart_product.product_id,
                    "coupon_value": 0,
                    "product_value": 0,
                    "is_combo": False,
                    "has_sub_products": False,
                    "transport_details": {},
                    "event_details": {}
                }
            )
        else:
            coupon_value_for_each_product = 0
            if total_coupon_value > 0:
                coupon_value_for_each_product = calculate_coupon_value(
                    total_coupon_value, product_details[each_cart_product.product_id]['price'],
                    total_products_value, each_cart_product.quantity)

            transport_data = get_transport_data(each_cart_product.product_id, transport_details)
            event_data = get_event_data(each_cart_product.product_id, event_details)

            cart_products_for_bookings[each_cart_product.cart_id].append({
                "product_id": each_cart_product.product_id,
                "quantity": each_cart_product.quantity,
                "size": each_cart_product.size,
                "parent_booked_product": None,
                "coupon_value": coupon_value_for_each_product,
                "product_value": product_price_values[each_cart_product.product_id]["discounted_price"],
                "is_combo": each_cart_product.is_combo,
                "has_sub_products": each_cart_product.has_sub_products,
                "transport_details": transport_data,
                "event_details": event_data
            })

    return cart_products_for_bookings


def calculate_coupon_value(total_coupon_value, product_value, total_products_value, quantity):
    return (float(total_coupon_value) / 100) * \
           ((float(product_value) / float(total_products_value)) * 100) * quantity


def calculate_total_products_value(cart_products, product_details, transport_details, event_details):
    group_product_details_by_type = defaultdict(dict)
    group_product_ids_by_type = defaultdict(list)

    for each_cart_product in cart_products:
        if not each_cart_product.hidden:
            product_type = product_details[each_cart_product.product_id]['type']

            transport_data = get_transport_data(each_cart_product.product_id, transport_details)
            event_data = get_event_data(each_cart_product.product_id, event_details)

            group_product_ids_by_type[product_type].append(each_cart_product.product_id)
            group_product_details_by_type[product_type].update(
                {
                    each_cart_product.product_id: {
                        "quantity": each_cart_product.quantity,
                        "size": each_cart_product.size,
                        "start_time": each_cart_product.cart.start_time,
                        "end_time": each_cart_product.cart.end_time,
                        "trip_type": transport_data["trip_type"],
                        "discount_percentage": product_details[each_cart_product.product_id]["discount"],
                        "km_limit_choosen": transport_data["km_limit_choosen"],
                        "event_prices": event_data["prices"],
                        "event_slot": event_data["slot"]
                    }
                }
            )

    product_price_values = get_product_price_values(group_product_ids_by_type, group_product_details_by_type)

    total_products_value = 0
    for each_product in cart_products:
        if not each_product.hidden:
            total_products_value += product_price_values[each_product.product_id]['discounted_price']

    return total_products_value, product_price_values


def get_transport_data(product_id, transport_details):
    if product_id in transport_details:
        transport_data = {
            "trip_type": transport_details[product_id].trip_type,
            "pickup_location": transport_details[product_id].pickup_location,
            "drop_location": transport_details[product_id].drop_location,
            "km_limit_choosen": transport_details[product_id].km_limit_choosen
        }
    else:
        transport_data = {
            "trip_type": "",
            "pickup_location": "",
            "drop_location": "",
            "km_limit_choosen": 0
        }

    return transport_data


def get_event_data(product_id, event_details):
    if product_id in event_details:
        total_price = 0
        for each_price in event_details.prices:
            total_price += each_price["price"] * each_price["quantity"]
        event_data = {
            "slot": event_details.slot,
            "name": event_details.name,
            "phone_no": event_details.phone_no,
            "alternate_no": event_details.alternate_no,
            "email": event_details.email,
            "prices": event_details.prices,
            "total_price": total_price
        }
    else:
        event_data = {
            "slot": "",
            "name": "",
            "phone_no": 0,
            "alternate_no": 0,
            "email": "",
            "prices": {},
            "total_price": 0
        }
    return event_data