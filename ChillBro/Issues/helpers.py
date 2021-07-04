import uuid
from django.conf import settings


def image_upload_to_issue(instance, filename):
    issue_id = instance.issue.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (issue_id, str(uuid.uuid4()), file_extension)
    return "static/images/issue/%s/%s" % (issue_id, new_filename)


def get_user_model():
    return settings.AUTH_USER_MODEL
