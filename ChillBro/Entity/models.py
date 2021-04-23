from django.db import models
from .constants import Status, EntityTypes, Cities
import uuid
from django.core.validators import MinLengthValidator
from .helpers import get_user_model
from django.utils import timezone
from .validations import validate_pan, validate_aadhar, validate_registration, validate_gst
from .helpers import image_upload_pan, image_upload_aadhar, image_upload_gst, image_upload_registration

class MyEntity(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=100)
    name = models.CharField(max_length=20, verbose_name="Name")
    type = models.CharField(max_length=20, choices=[(entity.name, entity.value) for entity in EntityTypes])
    status = models.CharField(max_length=20, choices=[(status.name, status.value) for status in Status],
                              default=Status.ONLINE.value)
    city = models.CharField(max_length=30, default=Cities.VSKP.value,
                            choices=[(city.name, city.value) for city in Cities], verbose_name="City")
    pincode = models.CharField(max_length=6, verbose_name="Pincode", validators=[MinLengthValidator(6)])
    active_from = models.DateTimeField(default=timezone.now)
    user_model = get_user_model()
    supervisor_id = models.ForeignKey(user_model, on_delete=models.CASCADE)
    pan_no = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_pan])
    registration_no = models.CharField(max_length=21, validators=[MinLengthValidator(21), validate_registration])
    gst_in = models.CharField(max_length=15, validators=[MinLengthValidator(15), validate_gst])
    aadhar_no = models.CharField(max_length=14, validators=[MinLengthValidator(14), validate_aadhar])
    pan_image = models.ImageField(upload_to=image_upload_pan)
    registration_image = models.ImageField(upload_to=image_upload_registration)
    gst_image = models.ImageField(upload_to=image_upload_gst)
    aadhar_image = models.ImageField(upload_to=image_upload_aadhar)

    def __str__(self):
        return self.name+' '+self.id


class BusinessClientEntity(models.Model):
    entity_id = models.ForeignKey('MyEntity', on_delete=models.CASCADE, verbose_name="Booking Id")
    user_model = get_user_model()
    business_client_id = models.ForeignKey(user_model, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("entity_id", "business_client_id"),)
