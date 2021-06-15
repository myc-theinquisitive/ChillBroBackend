from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from celery.decorators import task
from .models import Bookings
from django.core.exceptions import ObjectDoesNotExist
from .constants import BookingStatus


@task(name="cancel_booking_when_not_accepted")
def cancel_booking_if_not_accepted_by_business_client(booking_id):
    try:
        booking = Bookings.objects.get(id=booking_id)
    except ObjectDoesNotExist:
        logger.info("Invalid Booking Id: " + booking_id)
        return

    if booking.booking_status == BookingStatus.yet_to_approve.value:
        booking.booking_status = BookingStatus.business_client_not_acted.value
        booking.save()
        logger.info("Booking Cancelled as no action taken: " + booking_id + " " +
                    BookingStatus.business_client_not_acted.value)
    else:
        logger.info("Booking is already acted: " + booking_id + " " +
                    booking.booking_status)
