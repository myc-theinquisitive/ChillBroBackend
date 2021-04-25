from django.db import models
from .constants import Status, EntityTypes, Cities
import uuid
from django.core.validators import MinLengthValidator
from .helpers import get_user_model
from django.utils import timezone
from .validations import validate_pan, validate_aadhar, validate_registration, validate_gst
from .helpers import upload_aadhar_image_for_entity, upload_gst_image_for_entity, upload_pan_image_for_entity, upload_registration_image_for_entity

class MyEntity(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    name = models.CharField(max_length=100, verbose_name="Name")
    type = models.CharField(max_length=30, choices=[(entity.name, entity.value) for entity in EntityTypes])
    status = models.CharField(max_length=30, choices=[(status.name, status.value) for status in Status],
                              default=Status.ONLINE.value)
    address_id = models.CharField(max_length=36)
    active_from = models.DateTimeField(auto_now_add=True)
    user_model = get_user_model()
    pan_no = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_pan])
    registration_no = models.CharField(max_length=21, validators=[MinLengthValidator(21), validate_registration])
    gst_in = models.CharField(max_length=15, validators=[MinLengthValidator(15), validate_gst])
    aadhar_no = models.CharField(max_length=14, validators=[MinLengthValidator(14), validate_aadhar])
    pan_image = models.ImageField(upload_to=upload_pan_image_for_entity)
    registration_image = models.ImageField(upload_to=upload_registration_image_for_entity)
    gst_image = models.ImageField(upload_to=upload_gst_image_for_entity)
    aadhar_image = models.ImageField(upload_to=upload_aadhar_image_for_entity)

    def __str__(self):
        return self.name+' '+self.id



class BusinessClientEntity(models.Model):
    entity_id = models.ForeignKey('MyEntity', on_delete=models.CASCADE, verbose_name="Booking Id")
    user_model = get_user_model()
    business_client_id = models.ForeignKey(user_model, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("entity_id", "business_client_id"),)
