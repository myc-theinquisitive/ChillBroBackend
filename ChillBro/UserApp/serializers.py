from rest_framework import serializers
from .models import *
from .validations import validate_phone
from django.core.validators import MinLengthValidator
from .constants import Roles


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'email', 'password', 'phone_number', 'is_verified']


class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])


class NewBusinessClientSerializer(UserSerializer):
    business_name = serializers.CharField(max_length=100)
    secondary_contact = serializers.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])


class BusinessClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClient
        fields = "__all__"


class NewEmployeeSerializer(UserSerializer):
    entity_id = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(choices=[(role.name, role.value) for role in Roles])
    is_active = serializers.BooleanField()
    image = serializers.ImageField()


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

class EmployeeActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id','is_active']