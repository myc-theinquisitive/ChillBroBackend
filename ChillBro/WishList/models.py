from django.db import models
import uuid
from .constants import EntityType, ItemType, EntitySubType
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
    entity_sub_type = models.CharField(max_length=30, null=True, blank=True,
                                       choices=[(sub_type_of_entity.value, sub_type_of_entity.value)
                                                for sub_type_of_entity in EntitySubType])
    item_type = models.CharField(max_length=30,
                                 choices=[(type_of_item.value, type_of_item.value) for type_of_item in
                                          ItemType])

    # for product
    product_id = models.CharField(max_length=36, null=True, blank=True)

    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)
