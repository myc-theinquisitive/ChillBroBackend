from rest_framework import  serializers
from .models import ReferBusinessClient, SignUpRequest


class ReferBusinessClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferBusinessClient
        fields = "__all__"

class SignUpRequestSerialiser(serializers.ModelSerializer):
    class Meta:
        model = SignUpRequest
        fields = "__all__"
        readonly_fields = ('status')

class SignUpRequestApprovalSerialiser(serializers.ModelSerializer):
    class Meta:
        model = SignUpRequest
        fields = ('id','status')
