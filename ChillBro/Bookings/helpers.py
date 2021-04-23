from datetime import datetime, date
from django.utils.text import slugify
from django.conf import settings
import uuid


def getTodayDay():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def getTodayDate():
    today = date.today().strftime("%d")
    return int(today) - 1


def get_user_model():
    return settings.AUTH_USER_MODEL


def image_upload_to_user_id_proof(instance, filename):
    id = instance.booking.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/users_id_proof/%s/%s" % (id, new_filename)


def check_in_images(instance, filename):
    id = instance.check_in.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/check_in/%s/%s" % (id, new_filename)


def check_out_images(instance, filename):
    id = instance.check_out.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/check_out/%s/%s" % (id, new_filename)


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"
