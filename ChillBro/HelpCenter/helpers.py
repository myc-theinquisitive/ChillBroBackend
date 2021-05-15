import uuid
from django.conf import settings


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def upload_carousel_image(instance, filename):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/carousel/%s/%s" % (id, new_filename)
