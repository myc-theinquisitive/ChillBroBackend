from django.utils.text import slugify
import uuid
from django.conf import settings


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def upload_image_to_category(instance, filename):
    name = instance.category.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/Category/%s/%s" % (slug, new_filename)


def update_image_to_category_icon(instance, filename):
    name = instance.name
    basename, file_extension = filename.split(".")
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/Category/icons/%s/%s" % (name, new_filename)
