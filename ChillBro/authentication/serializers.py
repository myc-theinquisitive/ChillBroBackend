from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import OTPCode
from .validations import validate_phone


class SignupSerializer(serializers.Serializer):
    """
    Don't require email to be unique so visitor can signup multiple times,
    if misplace verification email.  Handle in view.
    """
    first_name = serializers.CharField(max_length=30, default='')
    last_name = serializers.CharField(max_length=30, default='')


class MailSignUpSerializer(SignupSerializer):
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, required=True)


class PhoneSignUpSerializer(SignupSerializer):
    phone_number = serializers.CharField(max_length=10, required=True,
                                         validators=[MinLengthValidator(10), validate_phone])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)


class PasswordResetVerifiedSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=40)
    password = serializers.CharField(max_length=128)


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)


class EmailChangeVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name')


class OTPCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPCode
        fields = '__all__'


class OTPValidateSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10)
    otp = serializers.CharField(max_length=6)


class OTPResendSerializer(OTPValidateSerializer):
    time = serializers.DateTimeField(default=timezone.now)
