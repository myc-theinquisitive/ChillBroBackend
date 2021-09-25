from django.utils.text import slugify
import uuid
from django.conf import settings


def image_upload_to_amenities(instance, filename):
    name = instance.name
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/Amenities/%s/%s" % (slug, new_filename)


class LatLong:
    def __init__(self, latitude, longitude):
        self.longitude = longitude
        self.latitude = latitude