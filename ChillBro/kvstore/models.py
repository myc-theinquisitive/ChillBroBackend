# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from kvstore.managers import TagManager


@python_2_unicode_compatible
class Tag(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey('content_type', 'object_id')
    key = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        db_index=True,
    )
    value = models.TextField(null=False)

    objects = TagManager()

    class Meta:
        # Enforce unique tag association per object
        unique_together = (('content_type', 'object_id', 'key',),)

    def __str__(self):
        return u'%s - %s - %s' % (self.content_object, self.key, self.value)
