from rest_framework import  serializers
from .models import ReferBusinessClient, SignUpRequest


class ReferBusinessClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferBusinessClient
        fields = "__all__"


class SignUpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignUpRequest
        fields = "__all__"
        read_only_fields = ('status', )


class SignUpRequestApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignUpRequest
        fields = ('id', 'status')
