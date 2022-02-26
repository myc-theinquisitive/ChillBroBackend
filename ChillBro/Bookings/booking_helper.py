from collections import defaultdict
from datetime import datetime
from django.conf import settings
from Bookings.constants import ProductBookingStatus
from Bookings.helpers import get_total_time_period
from Bookings.models import BookedProducts, Bookings, CheckInDetails, CheckOutDetails, CheckInImages
from Bookings.wrapper import create_refund_transaction, update_booking_transaction_in_payment, \
    get_product_id_wise_product_details


def cancel_booking(booking):
    # TODO: refund need to be handled
    # TODO: update payment amount to be paid to business client

    booked_products = BookedProducts.objects.select_related('booking').filter(booking=booking)
    booked_products.update(booking_status=ProductBookingStatus.cancelled.value)

    create_refund_transaction(
        {
            'booking_id': booking.id, 'entity_id': booking.entity_id,
            'entity_type': booking.entity_type, 'refund_amount': booking.total_money,
            'booking_date': booking.booking_date, 'booking_start': booking.start_time,
            'refund_reason': "Booking Cancelled"
        }
    )
    update_booking_transaction_in_payment(booking.id, True, 0, 0, 0)


def update_booking_status(booking_id, status):
    return Bookings.objects.filter(id=booking_id).update(booking_status=status)


def get_complete_booking_details_by_ids(booking_ids):
    bookings = Bookings.objects.filter(id__in=booking_ids)
    booked_products = BookedProducts.objects.filter(booking_id__in=booking_ids)
    booking_check_ins = CheckInDetails.objects.filter(booking_id__in=booking_ids)
    booking_check_outs = CheckOutDetails.objects.filter(booking_id__in=booking_ids)

    booking_id_wise_booked_products = defaultdict(list)
    product_ids = set()
    for booked_product in booked_products:
        product_ids.add(booked_product.product_id)
        booking_id_wise_booked_products[booked_product.booking_id].append(booked_product)
    product_id_wise_product_details = get_product_id_wise_product_details(list(product_ids))

    check_in_details = {}
    for check_in in booking_check_ins:
        check_in_details[check_in.booking_id] = check_in

    check_out_details = {}
    for check_out in booking_check_outs:
        check_out_details[check_out.booking_id] = check_out

    complete_bookings_details = []
    for booking in bookings:
        booking_dict = {
            'id': booking.id,
            'entity_type': booking.entity_type,
            'booked_at': booking.booking_date,
            'booking_status': booking.booking_status,
            'total_money': booking.total_money,
            'total_net_value': booking.total_net_value,
            'total_coupon_discount': booking.total_coupon_discount,
            'from_date': booking.start_time,
            'to_date': booking.end_time,
            'total_days': get_total_time_period(booking.end_time, booking.start_time),
            'ago': get_total_time_period(datetime.now(), booking.booking_date)
        }

        check_in_flag = True
        try:
            booking_dict['check_in'] = check_in_details[booking.id].check_in
        except KeyError:
            booking_dict['check_in'] = "Booking yet to start"
            booking_dict['check_out'] = "Booking yet to start"
            check_in_flag = False

        if check_in_flag:
            try:
                booking_dict['check_out'] = check_out_details[booking.id].check_out
            except KeyError:
                booking_dict['check_out'] = "Booking yet to end"

        booking_products_details = []
        for booked_product in booking_id_wise_booked_products[booking.id]:
            product_details = product_id_wise_product_details[booked_product.product_id]
            booking_products_details.append(
                {
                    "product_id": booked_product.product_id,
                    "name": product_details["name"],
                    "type": product_details["type"],
                    "product_value": booked_product.product_value,
                    "net_value": booked_product.net_value,
                    "coupon_value": booked_product.coupon_value,
                    "booked_quantity": booked_product.quantity
                }
            )
        booking_dict['products'] = booking_products_details
        complete_bookings_details.append(booking_dict)
    return complete_bookings_details


def get_check_in_details(check_in_object):
    response_data = {
        'is_caution_deposit_collected': True,
        'caution_amount': check_in_object.caution_amount
    }

    other_images = []
    check_in_images = CheckInImages.objects.filter(check_in_id=check_in_object.id)
    for check_in_image in check_in_images:
        image_url = check_in_image.image.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
        other_images.append(image_url)

    response_data['other_images'] = other_images

    return response_data
