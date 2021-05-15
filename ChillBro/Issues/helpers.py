import uuid
from django.conf import settings


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def image_upload_to_issue(instance, filename):
    issue_id = instance.issue.id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (issue_id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/issue/%s/%s" % (issue_id, new_filename)


def get_user_model():
    return settings.AUTH_USER_MODEL
