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
from .models import send_multi_format_email
from .serializers import LoginSerializer, OTPCreateSerializer, OTPValidateSerializer, \
    MailSignUpSerializer, PhoneSignUpSerializer
from .serializers import PasswordResetSerializer
from .serializers import PasswordResetVerifiedSerializer
from .serializers import EmailChangeSerializer
from .serializers import PasswordChangeSerializer
from .serializers import UserSerializer
import jwt

from .wrapper import sendOTP, check_business_client, check_employee, create_wallet


class Signup(APIView):
    permission_classes = (AllowAny, )
    mail_serializer_class = MailSignUpSerializer
    phone_serializer_class = PhoneSignUpSerializer

    def mailSignUp(self, serializer, email, password, first_name, last_name):
        must_validate_email = getattr(settings, "AUTH_VERIFICATION", True)
        email=email.lower().strip()
        try:
            user = get_user_model().objects.get(email=email)
            if user.is_verified:
                content = {'detail': _('Email address already taken.')}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Delete old signup codes
                signup_code = SignupCode.objects.get(user=user)
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass

        except get_user_model().DoesNotExist:
            user = get_user_model().objects.create_user(email=email)

        # Set user fields provided
        user.set_password(password)
        user.first_name = first_name.title().strip()
        user.last_name = last_name.title().strip()
        if not must_validate_email:
            user.is_verified = True
            send_multi_format_email('welcome_email',
                                    {'email': user.email, },
                                    target_email=user.email)
        user.save()

        create_wallet(user)

        if must_validate_email:
            # Create and associate signup code
            ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
            signup_code = SignupCode.objects.create_signup_code(user, ipaddr)
            signup_code.send_signup_email()

        content = {'email': email, 'first_name': first_name,
                   'last_name': last_name, 'message':'Verification mail has been sent to '+email}
        return Response(content, status=status.HTTP_201_CREATED)

    def phoneSignUp(self, serializer, phone_number, first_name, last_name):
        must_validate_phone = getattr(settings, "AUTH_VERIFICATION", True)

        try:
            user = get_user_model().objects.get(phone_number=phone_number)
            if user.is_verified:
                content = {'detail': _('Phone number already registered.')}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Delete old signup codes
                signup_code = SignupCode.objects.get(user=user)
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass

        except get_user_model().DoesNotExist:
            user = get_user_model().objects.create_user_by_phone(phone_number=phone_number)

        # Set user fields provided
        user.first_name = first_name.title().strip()
        user.last_name = last_name.title().strip()
        if not must_validate_phone:
            user.is_verified = True
            # send_multi_format_email('welcome_email',{'email': user.email, },target_email=user.email)

        user.save()

        create_wallet(user)

        if must_validate_phone:
            # Create and associate signup code
            ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
            signup_code = SignupCode.objects.create_signup_code(user, ipaddr)
            sendOTP(signup_code, phone_number)

        content = {'phone_number': phone_number, 'first_name': first_name,
                   'last_name': last_name, 'message':'OTP Sent to '+phone_number}
        return Response(content, status=status.HTTP_201_CREATED)

    def post(self, request, mail, phone, format=None):
        if mail:
            serializer = self.mail_serializer_class(data=request.data)
        else:
            serializer = self.phone_serializer_class(data=request.data)
        if serializer.is_valid():
            first_name = serializer.data['first_name']
            last_name = serializer.data['last_name']

            if mail:
                email = serializer.data['email']
                password = serializer.data['password']
                return self.mailSignUp(serializer, email, password, first_name, last_name)
            elif phone:
                phone_number = serializer.data['phone_number']
                return self.phoneSignUp(serializer, phone_number, first_name, last_name)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        code = request.GET.get('code', '')
        verified = SignupCode.objects.set_user_is_verified(code)

        if verified:
            try:
                signup_code = SignupCode.objects.get(code=code)
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass
            content = {'success': _('Email address verified.')}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'detail': _('Unable to verify user.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @csrf_exempt
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email'].lower().strip()
            password = serializer.data['password']
            user = authenticate(email=email, password=password)

            if user:
                if user.is_verified:
                    if user.is_active:
                        token, created = Token.objects.get_or_create(user=user)

                        user_type = "CUSTOMER"
                        if check_business_client(user):
                            user_type = "BUSINESS CLIENT"
                        elif check_employee(user):
                            user_type = "EMPLOYEE"

                        encoded = jwt.encode(
                            {'token': token.key}, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

                        response = Response(status=status.HTTP_200_OK)
                        response.set_cookie(key='token', value=encoded, httponly=True, samesite='strict', path='/')
                        response.data = {
                            'user': email,
                            'name': user.first_name,
                            'id': user.id,
                            "user_type": user_type,
                            'message': "Login Successful"
                        }
                        return response
                    else:
                        content = {'detail': _('User account not active.'),"user":""}
                        return Response(content,
                                        status=status.HTTP_401_UNAUTHORIZED)
                else:
                    content = {'detail':
                                   _('User account not verified.'),"user":""}
                    return Response(content, status=status.HTTP_401_UNAUTHORIZED)
            else:
                content = {'detail':
                               _('Unable to login with provided credentials.'),"user":""}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


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
            "message": "logged out"
        }
        return response


class PasswordReset(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']

            try:
                user = get_user_model().objects.get(email=email)

                # Delete all unused password reset codes
                PasswordResetCode.objects.filter(user=user).delete()

                if user.is_verified and user.is_active:
                    password_reset_code = \
                        PasswordResetCode.objects.create_password_reset_code(user)
                    password_reset_code.send_password_reset_email()
                    content = {'email': email, 'message':'Password reset link sent to '+email}
                    return Response(content, status=status.HTTP_201_CREATED)

            except get_user_model().DoesNotExist:
                pass

            # Since this is AllowAny, don't give away error.
            content = {'detail': _('Password reset not allowed.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class PasswordResetVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        code = request.GET.get('code', '')

        try:
            password_reset_code = PasswordResetCode.objects.get(code=code)

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

        if serializer.is_valid():
            code = serializer.data['code']
            password = serializer.data['password']

            try:
                password_reset_code = PasswordResetCode.objects.get(code=code)
                password_reset_code.user.set_password(password)
                password_reset_code.user.save()

                # Delete password reset code just used
                password_reset_code.delete()

                content = {'success': _('Password reset.')}
                return Response(content, status=status.HTTP_200_OK)
            except PasswordResetCode.DoesNotExist:
                content = {'detail': _('Unable to verify user.')}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class EmailChange(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmailChangeSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user

            # Delete all unused email change codes
            EmailChangeCode.objects.filter(user=user).delete()

            email_new = serializer.data['email']

            try:
                user_with_email = get_user_model().objects.get(email=email_new)
                if user_with_email.is_verified:
                    content = {'detail': _('Email address already taken.')}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # If the account with this email address is not verified,
                    # give this user a chance to verify and grab this email address
                    raise get_user_model().DoesNotExist

            except get_user_model().DoesNotExist:
                email_change_code = EmailChangeCode.objects.create_email_change_code(user, email_new)

                email_change_code.send_email_change_emails()

                content = {'email': email_new, 'message':'Verification link sent to '+email_new}
                return Response(content, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class EmailChangeVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        code = request.GET.get('code', '')

        try:
            # Check if the code exists.
            email_change_code = EmailChangeCode.objects.get(code=code)

            # Check if the code has expired.
            delta = date.today() - email_change_code.created_at.date()
            if delta.days > EmailChangeCode.objects.get_expiry_period():
                email_change_code.delete()
                raise EmailChangeCode.DoesNotExist()

            # Check if the email address is being used by a verified user.
            try:
                user_with_email = get_user_model().objects.get(email=email_change_code.email)
                if user_with_email.is_verified:
                    # Delete email change code since won't be used
                    email_change_code.delete()

                    content = {'detail': _('Email address already taken.')}
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

            content = {'success': _('Email address changed.')}
            return Response(content, status=status.HTTP_200_OK)
        except EmailChangeCode.DoesNotExist:
            content = {'detail': _('Unable to verify user.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class PasswordChange(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user
            email = user.email
            old_password = serializer.data['old_password']
            new_password = serializer.data['new_password']
            user = authenticate(email=email, password=old_password)
            if user:
                user.set_password(new_password)
                user.save()
            else:
                content = {"message":"Password Incorrect"}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            content = {'success': _('Password changed.')}
            return Response(content, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UserMe(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    # authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user).data)


def checkPhoneExists(phone):
    try:
        user = get_user_model().objects.get(phone_number=phone)
        return True
    except:
        return False

class OTPLogin(APIView):
    serializer_class = OTPCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone = request.data['phone']
            if checkPhoneExists(phone):
                serializer.save()
                sendOTP(serializer.data['otp'],phone)
                return Response({'otp': serializer.data['otp']}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Phone no. not registered"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPValidate(APIView):
    serializer_class = OTPValidateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        phone = request.data['phone']
        try:
            phone_user_object = OTPCode.objects.get(phone=request.data['phone'])
        except:
            return Response({"message", "Phone No. not found"}, status=status.HTTP_400_BAD_REQUEST)
        if phone_user_object.otp == request.data['otp']:
            now = datetime.datetime.now()

            if now < phone_user_object.expiry_time:
                try:
                    user = get_user_model().objects.get(phone_number=phone)
                except:
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
                    # return Response({"authenticate": True, "message": "Sucessfully OTP Validated", 'token': token.key},
                    #                 status=status.HTTP_200_OK)
                else:
                    content = {'detail': _('User account not active.'), "authenticate": False,
                               "message": "User not active"}
                    return Response(content,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"authenticate": True, "message": "OTP has been expired"})
        else:
            return Response({"authenticate": False, "message": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)


def random_string():
    return str(random.randint(100000, 999999))


class OTPResend(APIView):
    serializer_class = OTPCreateSerializer

    def put(self, request):
        phone = request.data['phone']
        try:
            phone_user_object = OTPCode.objects.get(phone=request.data['phone'])
        except:
            return Response({"message", "Phone No. not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not phone_user_object:
            return Response({'message': 'Phone no. not registered'}, status=status.HTTP_400_BAD_REQUEST)
        if (not checkPhoneExists(phone)):
            return Response({"message": "Phone no. not registered"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['otp'] = random_string()
        request.data['time'] = timezone.now()
        request.data['expiry_time'] = timezone.now() + timedelta(minutes=5)
        serializer = self.serializer_class(phone_user_object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
