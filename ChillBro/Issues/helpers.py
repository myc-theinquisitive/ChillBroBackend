import uuid
from django.conf import settings
from .constants import EntityType, SupportStatus


def image_upload_to_issue(instance, filename):
    issue_id = instance.issue.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (issue_id, str(uuid.uuid4()), file_extension)
    return "static/images/issue/%s/%s" % (issue_id, new_filename)


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_entity_types_filter(entity_filter):
    if len(entity_filter) == 0:
        entities = [entity_type.value for entity_type in EntityType]
        return entities
    return entity_filter


def get_user_status_filters(status):
    if len(status) == 0:
        return [status.value for status in SupportStatus]
    status_results = set()
    if "PENDING" in status:
        status_results.add(SupportStatus.TODO.value)
        status_results.add(SupportStatus.IN_PROGRESS.value)
    if "COMPLETED" in status:
        status_results.add(SupportStatus.DONE.value)
    return list(status_results)


def convert_support_status_to_user_status(status):
    if status == SupportStatus.DONE.value:
        return "COMPLETED"
    else:
        return "PENDING"
