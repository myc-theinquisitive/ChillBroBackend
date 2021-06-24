from django.utils.text import slugify
import uuid
from django.conf import settings


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def image_upload_to_travel_agency(instance, filename):
    name = instance.travel_agency.name
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/TravelAgency/%s/%s" % (slug, new_filename)

def upload_image_to_travel_characteristics(instance, filename):
    name = instance.name
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/TravelAgency/characteristics/%s/%s" % (slug, new_filename)
