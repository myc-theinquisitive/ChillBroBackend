from rest_framework import serializers

from .models import BusinessClientQuotation

class BusinessClientQuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientQuotation
        fields = '__all__'

