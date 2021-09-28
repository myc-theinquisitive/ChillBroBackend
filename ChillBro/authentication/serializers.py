from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import OTPCode
from ChillBro.validations import validate_phone, validate_email


def email_required(obj):
    obj_dict = dict(obj)
    email = obj_dict["email"] if "email" in obj_dict else None
    if not email:
        raise serializers.ValidationError("Email is required")


def phone_number_required(obj):
    obj_dict = dict(obj)
    phone_number = obj_dict["phone_number"] if "phone_number" in obj_dict else None
    if not phone_number:
        raise serializers.ValidationError("Phone Number is required")


def email_or_phone_number_required(obj):
    obj_dict = dict(obj)
    phone_number = obj_dict["phone_number"] if "phone_number" in obj_dict else None
    email = obj_dict["email"] if "email" in obj_dict else None
    if not phone_number and not email:
        raise serializers.ValidationError("Email or Phone Number is required")


class SignupSerializer(serializers.Serializer):
    """
    Don't require email to be unique so visitor can signup multiple times,
    if misplace verification email.  Handle in view.
    """
    first_name = serializers.CharField(max_length=30, default='')
    last_name = serializers.CharField(max_length=30, default='')


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=10, validators=[MinLengthValidator(10), validate_phone],
        required=False, allow_blank=True, allow_null=True)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, validators=[validate_email],
                                   required=False, allow_blank=True, allow_null=True)


class MailOrPhoneNumberSerializer(PhoneNumberSerializer, EmailSerializer):

    class Meta:
        validators = [email_or_phone_number_required]


class MailOrPhoneNumberExistserializer(MailOrPhoneNumberSerializer):
    pass


class MailSignUpSerializer(SignupSerializer, EmailSerializer):
    password = serializers.CharField(max_length=128,  default="hi")

    class Meta:
        validators = [email_required]


class PhoneSignUpSerializer(SignupSerializer, PhoneNumberSerializer):

    class Meta:
        validators = [phone_number_required]


class LoginSerializer(EmailSerializer):
    password = serializers.CharField(max_length=128)

    class Meta:
        validators = [email_required]


class PasswordResetSerializer(MailOrPhoneNumberSerializer):
    pass


class PasswordResetVerifiedSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=40)
    password = serializers.CharField(max_length=128)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)


class EmailChangeSerializer(EmailSerializer):

    class Meta:
        validators = [email_required]


class EmailChangeVerifySerializer(EmailSerializer):

    class Meta:
        validators = [email_required]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'id')


class OTPCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPCode
        fields = '__all__'


class OTPValidateSerializer(PhoneNumberSerializer):
    otp = serializers.CharField(max_length=6)

    class Meta:
        validators = [phone_number_required]


class OTPResendSerializer(OTPValidateSerializer):
    time = serializers.DateTimeField(default=timezone.now)
