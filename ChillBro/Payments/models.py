from django.db import models
from datetime import datetime
import uuid
from .constants import PayMode, PayStatus, EntityType


# Create your models here.
def getId():
    return str(uuid.uuid4())


class TransactionDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.CharField(max_length=36)
    transaction_id = models.CharField(max_length=50)
    utr = models.CharField(max_length=50)
    mode = models.CharField(max_length=10, choices=[(mode.value, mode.value) for mode in PayMode],
                            default=PayMode.upi.value)
    transaction_date = models.DateTimeField(default=datetime.now)
    entity_id = models.CharField(max_length=36)
    total_money = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    total_net_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    entity_type = models.CharField(max_length=30,
                                   choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in
                                            EntityType], default=EntityType.hotels.value)
    payment_status = models.CharField(max_length=30,
                                     choices=[(pay_status.value, pay_status.value) for pay_status in PayStatus],
                                     default=PayStatus.pending.value)
    booking_date = models.DateTimeField()

    def __str__(self):
        return str(self.booking_id)

    class Meta:
        unique_together = ('booking_id','booking_id')
