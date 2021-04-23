from rest_framework import serializers
from .models import *


class TransactionDetailsSerializer(serializers.Serializer):
    class Meta:
        model = TransactionDetails
        fields = '__all__'
