from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *


urlpatterns = [
    # signup
    path('signup-validate/', MailOrPhoneNumberExists.as_view()),
    path('mail-signup/', Signup.as_view(), {"mail": True, "phone": False}),
    path('phone-signup/', Signup.as_view(), {"mail": False, "phone": True}),
    path('signup/verify/', SignupVerify.as_view()),

    path('login/', Login.as_view()),
    path('logout/', Logout.as_view()),

    # Password Change
    path('password/reset/', PasswordReset.as_view()),
    path('password/reset/verify/', PasswordResetVerify.as_view()),
    path('password/reset/verified/', PasswordResetVerified.as_view()),

    # Email Change
    path('email/change/', EmailChange.as_view()),
    path('email/change/verify/', EmailChangeVerify.as_view()),

    # Profile
    path('users/me/', UserMe.as_view()),
    path('password/change/', PasswordChange.as_view()),

    # OTP login
    path('otp/login/', OTPLogin.as_view()),
    path('otp/validate/', OTPValidate.as_view()),
    path('otp/resend/', OTPResend.as_view())
]


urlpatterns = format_suffix_patterns(urlpatterns)