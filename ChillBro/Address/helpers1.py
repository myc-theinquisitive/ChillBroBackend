import uuid


def upload_image_to_city_icon(instance, filename):
    name = instance.name
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/Cities/%s/%s" % (name, new_filename)