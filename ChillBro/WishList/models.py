from django.db import models
import uuid
from .constants import EntityType
from .helpers import *
from datetime import datetime


def get_id():
    return str(uuid.uuid4())


class WishList(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(max_length=30,
                                   choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in
                                            EntityType])

    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=36)
    created_at = models.DateTimeField(default=datetime.now)
