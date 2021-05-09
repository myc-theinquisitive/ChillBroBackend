import uuid


def upload_carousel_image(instance, filename):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/carousel/%s/%s" % (id, new_filename)
