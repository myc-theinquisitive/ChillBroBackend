import uuid

def image_upload_to_review(instance, filename):
    id = instance.review_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/review/%s/%s" % (id, new_filename)
