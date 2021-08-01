from rest_framework import serializers
from .models import *
from .validations import validate_phone
from django.core.validators import MinLengthValidator


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'email', 'password', 'phone_number', 'is_verified']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'email', 'password', 'gender', 'phone_number', 'is_verified']


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
    role = serializers.CharField(max_length=30)
    is_active = serializers.BooleanField()
    images = serializers.ListField(
        allow_empty=True,
        child=serializers.ImageField()
    )


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class EmployeeActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'is_active']


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = '__all__'

    @staticmethod
    def bulk_create(employee_images):
        all_images = []
        for image in employee_images:
            each_image = EmployeeImage(
                employee=image['employee'],
                image=image['image']
            )
            all_images.append(each_image)
        EmployeeImage.objects.bulk_create(all_images)
