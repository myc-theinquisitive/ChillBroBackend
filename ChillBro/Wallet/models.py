from django.core.validators import MinValueValidator
from django.db import models
from .constants import TransactionType
from .helpers import get_user_model
import uuid

class Wallet(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0,validators=[MinValueValidator(0)])
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)


class WalletTransaction(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])
    transaction_type = models.CharField(max_length=10, choices=[(type.name, type.value) for type in TransactionType])
    transaction_id = models.CharField(max_length=36,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)