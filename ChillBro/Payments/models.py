from django.db import models
from datetime import datetime
import uuid
from .constants import PayMode


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

    def __str__(self):
        return str(self.booking_id)
