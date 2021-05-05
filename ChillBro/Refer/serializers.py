from rest_framework import  serializers
from .models import ReferBusinessClient


class ReferBusinessClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferBusinessClient
        fields = "__all__"