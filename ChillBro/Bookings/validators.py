from collections import defaultdict
from datetime import datetime
from .booking_calendar_helper import get_total_bookings_count_of_product_in_duration
from .helpers import get_date_format
from .wrapper import get_product_id_wise_product_details


def validate_booking_product_availability(actual_product_details, booking_products_list, start_time, end_time):
    is_valid = True
    errors = defaultdict(list)

    for booking_product in booking_products_list:
        product_id = booking_product['product_id']
        has_sizes = actual_product_details[product_id]['has_sizes']
        quantity_unlimited = actual_product_details[product_id]['quantity_unlimited']
        if not quantity_unlimited:
            if has_sizes:
                product_sizes_details = actual_product_details[product_id]['size_products']

                total_quantity = product_sizes_details[booking_product['size']]
            else:
                total_quantity = actual_product_details[product_id]['quantity']

            previous_bookings_count = get_total_bookings_count_of_product_in_duration(
                product_id, start_time, end_time, booking_product['size'])
            if is_valid and total_quantity - previous_bookings_count < booking_product['quantity']:
                is_valid = False
                if total_quantity - previous_bookings_count == 0:
                    errors[product_id].append("Sorry, No products are available")
                else:
                    errors[product_id].append(
                        "Sorry, only {} products are available".format(total_quantity - previous_bookings_count))
    return is_valid, errors


def validate_start_end_time(start_time, end_time):
    is_valid = True
    errors = defaultdict(list)
    current_time = datetime.now()
    if current_time.strftime(get_date_format()) >= start_time:
        is_valid = False
        errors["booking"].append("Start time should be greater than current time")
    # TODO: we cannot compare two date strings here. It will give invalid result
    if start_time >= end_time:
        is_valid = False
        errors["booking"].append("End time should be less than start time")

    return is_valid, errors


def validate_booking_product_details(actual_product_details, booking_products_list, start_time, end_time):
    is_valid, errors = validate_start_end_time(start_time, end_time)

    for booking_product in booking_products_list:
        product_id = booking_product['product_id']
        if booking_product['quantity'] <= 0:
            is_valid = False
            errors[product_id].append("Quantity should be greater than 0")

        has_sizes = actual_product_details[product_id]['has_sizes']
        if has_sizes:
            product_sizes_details = actual_product_details[product_id]['size_products']
            if not booking_product['size'] in product_sizes_details:
                is_valid = False
                errors[product_id].append("Invalid Size")

    return is_valid, errors


def validate_booking_details(booking_products_list, start_time, end_time):
    product_ids = []
    for product in booking_products_list:
        product_ids.append(product['product_id'])
    actual_product_details = get_product_id_wise_product_details(product_ids)

    is_valid, errors = validate_booking_product_details(
        actual_product_details, booking_products_list, start_time, end_time)
    if not is_valid:
        return is_valid, errors

    return validate_booking_product_availability(actual_product_details, booking_products_list, start_time, end_time)
