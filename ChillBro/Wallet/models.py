from django.core.validators import MinValueValidator
from django.db import models
from .constants import TransactionType, RewardType
from .helpers import get_user_model
import uuid


def get_id():
    return str(uuid.uuid4())


class Wallet(models.Model):
    user_model = get_user_model()
    id = models.CharField(primary_key=True, default=get_id, editable=False, max_length=36)
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])


class WalletTransaction(models.Model):
    user_model = get_user_model()
    id = models.CharField(primary_key=True, default=get_id, editable=False, max_length=36)
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])
    # unique for this wallet transaction CREDIT / DEBIT
    transaction_type = models.CharField(max_length=10, choices=[(type.name, type.value) for type in TransactionType])

    # Booking or other transaction for which reward is earned
    related_id = models.CharField(max_length=36)
    reward_type = models.CharField(max_length=30, choices=[(type.name, type.value) for type in RewardType],
                                   default=RewardType.BOOKING.value)

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
