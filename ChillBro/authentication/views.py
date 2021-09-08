from django.utils import timezone
import datetime, random
from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SignupCode, EmailChangeCode, PasswordResetCode, OTPCode
from .tasks import send_multi_format_email
from .serializers import LoginSerializer, OTPCreateSerializer, OTPValidateSerializer, \
    MailSignUpSerializer, PhoneSignUpSerializer, MailOrPhoneNumberSerializer
from .serializers import PasswordResetSerializer
from .serializers import PasswordResetVerifiedSerializer
from .serializers import EmailChangeSerializer
from .serializers import PasswordChangeSerializer
from .serializers import UserSerializer
import jwt
from .wrapper import sendOTP, check_business_client, check_employee, create_wallet
from ChillBro.validations import validate_phone, validate_email
from django.db.models import ObjectDoesNotExist

from UserApp.models import MyUser


def generate_cookie(user, response):
    token, created = Token.objects.get_or_create(user=user)
    encoded = jwt.encode(
        {'token': token.key}, settings.SECRET_KEY, algorithm='HS256')
    response.set_cookie(key='token', value=encoded, httponly=True, samesite='strict', path='/')
    return response


class MailOrPhoneNumberExists(APIView):
    permission_classes = (AllowAny,)
    serializer = MailOrPhoneNumberSerializer

    @staticmethod
    def check_email_exists(email):
        return get_user_model().objects.filter(email=email).exists()

    @staticmethod
    def check_phone_number_exists(phone_number):
        return get_user_model().objects.filter(phone_number=phone_number).exists()

    def post(self, request):
        serializer = self.serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.data["email"]
        phone_number = serializer.data["phone_number"]

        is_email_valid = is_phone_number_valid = False
        if email:
            is_email_valid = not self.check_email_exists(email)
        if phone_number:
            is_phone_number_valid = not self.check_phone_number_exists(phone_number)

        if is_email_valid or is_phone_number_valid:
            return Response({"message": "Email or Phone Number is valid"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email or Phone Number already exists"}, status=status.HTTP_400_BAD_REQUEST)


class Signup(APIView):
    permission_classes = (AllowAny,)
    mail_serializer_class = MailSignUpSerializer
    phone_serializer_class = PhoneSignUpSerializer

    @staticmethod
    def delete_signup_codes(user):
        try:
            # Delete old signup codes
            signup_code = SignupCode.objects.get(user=user)
            signup_code.delete()
        except SignupCode.DoesNotExist:
            pass

    def mail_sign_up(self, serializer, email, password, first_name, last_name):
        must_validate_email = getattr(settings, "AUTH_VERIFICATION", True)
        email = email.lower().strip()
        try:
            user = get_user_model().objects.get(email=email)
            if user.is_verified:
                content = {'message': 'Email address already taken.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            self.delete_signup_codes(user)
        except get_user_model().DoesNotExist:
            user = get_user_model().objects.create_user(email=email)

        # Set user fields provided
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        if not must_validate_email:
            user.is_verified = True
            # send_multi_format_email.delay('welcome_email', {'email': user.email, }, target_email=user.email)
            send_multi_format_email('welcome_email', {'email': user.email, }, target_email=user.email)

        user.save()
        create_wallet(user)

        if must_validate_email:
            # Create and associate signup code
            ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
            signup_code = SignupCode.objects.create_signup_code(user, ipaddr)
            signup_code.send_signup_email()

        content = {'email': email, 'first_name': first_name,
                   'last_name': last_name, 'message': 'Verification mail has been sent to ' + email}
        return Response(content, status=status.HTTP_201_CREATED)

    def phone_sign_up(self, serializer, phone_number, first_name, last_name):
        must_validate_phone = getattr(settings, "AUTH_VERIFICATION", True)

        try:
            user = get_user_model().objects.get(phone_number=phone_number)
            if user.is_verified:
                content = {'message': 'Phone number already registered.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.delete()
                user = get_user_model().objects.create_user_by_phone(phone_number=phone_number)
            self.delete_signup_codes(user)
        except get_user_model().DoesNotExist:
            user = get_user_model().objects.create_user_by_phone(phone_number=phone_number)

        # Set user fields provided
        user.first_name = first_name
        user.last_name = last_name
        if not must_validate_phone:
            user.is_verified = True
            send_multi_format_email('welcome_email', {'email': user.email, }, target_email=user.email)

        user.save()
        create_wallet(user)

        if must_validate_phone:
            # Create and associate signup code
            ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
            signup_code = SignupCode.objects.create_signup_code(user, ipaddr)
            sendOTP(signup_code, phone_number)

        content = {'phone_number': phone_number, 'first_name': first_name,
                   'last_name': last_name, 'message': 'OTP Sent to ' + phone_number, 'otp': str(signup_code)}
        return Response(content, status=status.HTTP_201_CREATED)

    def post(self, request, mail, phone, format=None):
        if mail:
            serializer = self.mail_serializer_class(data=request.data)
        else:
            serializer = self.phone_serializer_class(data=request.data)

        if serializer.is_valid():
            first_name = serializer.data['first_name'].title().strip()
            last_name = serializer.data['last_name'].title().strip()

            if mail:
                email = serializer.data['email']
                password = serializer.data['password']
                return self.mail_sign_up(serializer, email, password, first_name, last_name)
            elif phone:
                phone_number = serializer.data['phone_number']
                return self.phone_sign_up(serializer, phone_number, first_name, last_name)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def checkAndGetUserId(request):
    user_id = None
    if 'otp' not in request.data:
        return Response({'message': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST), False
    if 'email' not in request.data and 'phone_number' not in request.data:
        return Response({'message': 'Email or Phone number is required'}, status=status.HTTP_400_BAD_REQUEST), False
    code = request.data['otp']
    email = request.data['email'] if 'email' in request.data else None
    phone_number = request.data['phone_number'] if 'phone_number' in request.data else None

    if phone_number:
        try:
            user = get_user_model().objects.get(phone=phone_number)
        except get_user_model().DoesNotExist:
            return Response({'message': "Can't verify", 'error': 'Invalid Phone number'}, 400), False

    if email:
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response({'message': "Can't verify", 'error': 'Invalid Email'}, 400), False

    return user, True


class SignupVerify(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        response, is_valid = checkAndGetUserId(request)
        if not is_valid:
            return response
        user_id = response.id
        code = request.data['otp']

        try:
            signup_code = SignupCode.objects.get(code=code, user_id=user_id)
            signup_code.user.is_verified = True
            signup_code.user.save()
            user = signup_code.user
            signup_code.delete()

            response = Response(status=status.HTTP_200_OK)
            response = generate_cookie(user, response)
            response.data = {'message': 'User verified successfully'}
            return response
        except SignupCode.DoesNotExist:
            content = {'message': 'Unable to verify user'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @csrf_exempt
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.data['email'].lower().strip()
        password = serializer.data['password']
        user = authenticate(email=email, password=password)

        if not user:
            content = {'message': 'Unable to login with provided credentials.'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:
            content = {'detail': 'User account is not verified.'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            content = {'detail': 'User account is not active.'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        user_type = "CUSTOMER"
        if user.is_superuser:
            user_type = "Super Admin"
        elif check_business_client(user):
            user_type = "BUSINESS CLIENT"
        elif check_employee(user):
            user_type = "EMPLOYEE"

        response = Response(status=status.HTTP_200_OK)
        response = generate_cookie(user, response)
        response.data = {
            'user': email,
            'name': user.first_name,
            'id': user.id,
            "user_type": user_type,
            'message': "Login Successful"
        }
        return response


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Remove all auth tokens owned by request.user.
        """
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('token')
        response.data = {
            "message": "Logged out successfully."
        }
        return response


# TODO: Handle cases when the generated code already exists in the db
class PasswordReset(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = request.data['email'] if 'email' in request.data else None
        phone_number = request.data['phone_number'] if 'phone_number' in request.data else None

        user = None
        if phone_number:
            try:
                user = get_user_model().objects.get(phone=phone_number)
            except get_user_model().DoesNotExist:
                return Response({'message': "Can't reset password", 'error': 'Invalid Phone number'}, 400)

        if email:
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return Response({'message': "Can't reset password", 'error': 'Invalid Email'}, 400)

        phone_number = user.phone_number
        # Delete all unused password reset codes
        PasswordResetCode.objects.filter(user=user).delete()

        if user.is_verified and user.is_active:
            password_reset_code = \
                PasswordResetCode.objects.create_password_reset_code(user)
            password_reset_code.send_password_reset_email()
            sendOTP(password_reset_code, phone_number)
            content = {'message': 'OTP sent successfully'}
            return Response(content, status=status.HTTP_201_CREATED)

        # Since this is AllowAny, don't give away error.
        content = {'message': 'Password reset not allowed.'}
        return Response(content)


# TODO: what is this API for??
class PasswordResetVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):

        response, is_valid = checkAndGetUserId(request)
        if not is_valid:
            return response
        user = response
        code = request.data['code']

        try:
            password_reset_code = PasswordResetCode.objects.get(code=code, user=user)

            # Delete password reset code if older than expiry period
            delta = date.today() - password_reset_code.created_at.date()
            if delta.days > PasswordResetCode.objects.get_expiry_period():
                password_reset_code.delete()
                raise PasswordResetCode.DoesNotExist()

            content = {'success': _('Email address verified.')}
            return Response(content, status=status.HTTP_200_OK)
        except PasswordResetCode.DoesNotExist:
            content = {'detail': _('Unable to verify user.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetVerified(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetVerifiedSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response, is_valid = checkAndGetUserId(request)
        if not is_valid:
            return response
        user_id = response.id

        code = serializer.data['code']
        password = serializer.data['password']

        try:
            password_reset_code = PasswordResetCode.objects.get(code=code, user_id=user_id)
            password_reset_code.user.set_password(password)
            password_reset_code.user.save()

            # Delete password reset code just used
            password_reset_code.delete()

            content = {'message': 'Password reset successfully.'}
            return Response(content, status=status.HTTP_200_OK)
        except PasswordResetCode.DoesNotExist:
            content = {'message': 'Unable to verify user.', 'error': 'Invalid code'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class EmailChange(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmailChangeSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # Delete all unused email change codes
        EmailChangeCode.objects.filter(user=user).delete()

        email_new = serializer.data['email']
        try:
            user_with_email = get_user_model().objects.get(email=email_new)
            if user_with_email.is_verified:
                content = {'message': 'Email address already taken.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise get_user_model().DoesNotExist

        except get_user_model().DoesNotExist:
            email_change_code = EmailChangeCode.objects.create_email_change_code(user, email_new)
            email_change_code.send_email_change_emails()

            content = {'email': email_new, 'message': 'Verification link sent to ' + email_new}
            return Response(content, status=status.HTTP_201_CREATED)


class EmailChangeVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        code = request.GET.get('code', '')

        try:
            # Check if the code exists.
            email_change_code = EmailChangeCode.objects.get(code=code)
        except EmailChangeCode.DoesNotExist:
            content = {'message': "Can't update Email.", 'error': 'Invalid Code'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # Check if the code has expired.
        delta = date.today() - email_change_code.created_at.date()
        if delta.days > EmailChangeCode.objects.get_expiry_period():
            content = {'message': "Can't update Email.", 'error': 'Code Expired, Try again.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email address is being used by a verified user.
        try:
            user_with_email = get_user_model().objects.get(email=email_change_code.email)
            if user_with_email.is_verified:
                # Delete email change code since won't be used
                email_change_code.delete()
                content = {'message': "Can't update Email.", 'error': 'Email address already taken.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If the account with this email address is not verified,
                # delete the account (and signup code) because the email
                # address will be used for the user who just verified.
                user_with_email.delete()

        except get_user_model().DoesNotExist:
            pass

        # If all is well, change the email address.
        email_change_code.user.email = email_change_code.email
        email_change_code.user.save()

        # Delete email change code just used
        email_change_code.delete()

        content = {'message': 'Email address changed successfully.'}
        return Response(content, status=status.HTTP_200_OK)


class PasswordChange(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        email = user.email
        old_password = serializer.data['old_password']
        new_password = serializer.data['new_password']
        user = authenticate(email=email, password=old_password)
        if user:
            user.set_password(new_password)
            user.save()
        else:
            content = {"message": "Can't update password", "error": "Invalid Old Password"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        content = {'message': 'Password changed successfully.'}
        return Response(content, status=status.HTTP_200_OK)


class UserMe(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        response_data = self.serializer_class(request.user).data
        return Response(response_data, status=status.HTTP_200_OK)


class OTPLogin(APIView):
    serializer_class = OTPCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = request.data['phone']
        if not MailOrPhoneNumberExists.check_phone_number_exists(phone):
            return Response({"message": "Phone no. not registered"}, status=status.HTTP_404_NOT_FOUND)

        serializer.save()
        sendOTP(serializer.data['otp'], phone)
        return Response({'otp': serializer.data['otp']}, status=status.HTTP_200_OK)


class OTPValidate(APIView):
    serializer_class = OTPValidateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        phone = request.data['phone']
        try:
            phone_user_object = OTPCode.objects.get(phone=request.data['phone'])
        except ObjectDoesNotExist:
            return Response({"message", "Phone No. not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not phone_user_object.otp == request.data['otp']:
            return Response({"authenticate": False, "message": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

        now = datetime.datetime.now()
        if now >= phone_user_object.expiry_time:
            return Response({"authenticate": True, "message": "OTP has been expired"})

        try:
            user = get_user_model().objects.get(phone_number=phone)
        except ObjectDoesNotExist:
            return Response({"message": "Phone No. not registered"}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            user.is_verified = True

            token, created = Token.objects.get_or_create(user=user)

            encoded = jwt.encode(
                {'token': token.key}, settings.SECRET_KEY, algorithm='HS256')

            response = Response(status=status.HTTP_200_OK)
            response.set_cookie(key='token', value=encoded, httponly=True, samesite='strict', path='/')
            response.data = {
                "authenticate": True,
                "message": "Successfully OTP Validated",
            }
            return response
        else:
            content = {'detail': _('User account not active.'), "authenticate": False,
                       "message": "User not active"}
            return Response(content,
                            status=status.HTTP_400_BAD_REQUEST)


def random_string():
    return str(random.randint(100000, 999999))


class OTPResend(APIView):
    serializer_class = OTPCreateSerializer

    def put(self, request):
        phone = request.data['phone']
        try:
            phone_user_object = OTPCode.objects.get(phone=request.data['phone'])
        except ObjectDoesNotExist:
            return Response({"message", "Phone No. not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not MailOrPhoneNumberExists.check_phone_number_exists(phone):
            return Response({"message": "Phone no. not registered"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['otp'] = random_string()
        request.data['time'] = timezone.now()
        request.data['expiry_time'] = timezone.now() + timedelta(minutes=5)
        serializer = self.serializer_class(phone_user_object, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
