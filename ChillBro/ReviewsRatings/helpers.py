import uuid
from django.conf import settings
from .constants import *
from ChillBro.constants import *
from ChillBro.helpers import get_time_period


def image_upload_to_review(instance, filename):
    id = instance.review_id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/review/%s/%s" % (id, new_filename)


def get_entity_type(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities


def get_rating_filters(rating_filter):
    ratings = [rating for rating in range(1, 6)]
    if len(rating_filter) == 0:
        return ratings
    return rating_filter


def get_bc_app_feedback_categories(category_filters):
    categories = [category.value for category in BCAppFeedbackCategory]
    if len(category_filters) == 0:
        return categories
    if category_filters[0] == "ALL":
        return categories
    return category_filters
