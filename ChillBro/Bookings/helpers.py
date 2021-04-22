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
    name = instance.id
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/users_id_proof/%s/%s" % (slug, new_filename)
