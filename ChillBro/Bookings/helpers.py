from django.conf import settings
import uuid
from .constants import *
from ChillBro.helpers import get_time_period, get_previous_time_period


def get_user_model():
    return settings.AUTH_USER_MODEL


def image_upload_to_user_id_proof(instance, filename):
    id = instance.booking.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/users_id_proof/%s/%s" % (id, new_filename)


def image_upload_to_check_in(instance, filename):
    id = instance.check_in.booking_id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/check_in/%s/%s" % (id, new_filename)


def image_upload_to_check_out(instance, filename):
    id = instance.check_out.booking_id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/check_out/%s/%s" % (id, new_filename)


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_entity_types_filter(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) == 0:
        return entities
    return entity_filter


def get_status_filters(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status


def get_after_booking_confirmation_status_filters(status):
    if len(status) == 0:
        return BookingStatus.after_booking_confirmation_enums()
    return status


def get_total_time_period(from_date, to_date):
    days = from_date - to_date
    seconds = int(days.total_seconds())
    if seconds < 60:
        return "1 min"
    else:
        minutes = seconds // 60
        if minutes < 60:
            return str(minutes) + " minutes"
        else:
            hours = minutes // 60
            if hours < 24:
                return str(hours) + " hours"
            else:
                days = hours // 24
                return str(days) + " days"
