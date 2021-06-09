from django.utils.text import slugify
import uuid
from django.conf import settings


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def image_upload_to_travel_package(instance, filename):
    name = instance.travel_package.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/TravelPackage/%s/%s" % (slug, new_filename)
