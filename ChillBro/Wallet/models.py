from django.core.validators import MinValueValidator
from django.db import models
from .constants import Types
from .helpers import get_user_model


class Wallet(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0,validators=[MinValueValidator(0)])

class WalletTransaction(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])
    transaction_type = models.CharField(max_length=10, choices=[(type.name, type.value) for type in Types])
    trans_id = models.CharField(max_length=36,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=100)