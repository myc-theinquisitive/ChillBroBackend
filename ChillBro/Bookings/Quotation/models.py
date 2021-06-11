from django.db import models
import uuid


class BusinessClientQuotation(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    bc_id = models.CharField(max_length=36)
    vehicle_name = models.CharField(max_length=40)
    amount = models.IntegerField()
    booking_id = models.CharField(max_length=36)

    class Meta:
        unique_together = ("bc_id","booking_id")


class Quotation(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    booking_id = models.CharField(max_length=36)