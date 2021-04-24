from django.utils.text import slugify
import uuid


def uploadImageToCategoryIcons(instance, filename):
    name = instance.category.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/Category/%s/%s" % (slug, new_filename)


def iconUrlImage(instance, filename):
    name = instance.id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (name, str(uuid.uuid4()), file_extension)
    return "static/images/Category/icons/%s/%s" % (name, new_filename)