from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *


urlpatterns = [
    path('signup/', Signup.as_view(), name='authemail-signup'),
    path('signup/verify/', SignupVerify.as_view(),
         name='authemail-signup-verify'),

    path('login/', Login.as_view(), name='authemail-login'),
    path('logout/', Logout.as_view(), name='authemail-logout'),

    path('password/reset/', PasswordReset.as_view(),
         name='authemail-password-reset'),
    path('password/reset/verify/', PasswordResetVerify.as_view(),
         name='authemail-password-reset-verify'),
    path('password/reset/verified/', PasswordResetVerified.as_view(),
         name='authemail-password-reset-verified'),

    path('email/change/', EmailChange.as_view(),
         name='authemail-email-change'),
    path('email/change/verify/', EmailChangeVerify.as_view(),
         name='authemail-email-change-verify'),

    path('password/change/', PasswordChange.as_view(),
         name='authemail-password-change'),

    path('users/me/', UserMe.as_view(), name='authemail-me'),
    path('otp/login/',OTPLogin.as_view(),name='otplogin'),
    path('otp/validate/',OTPValidate.as_view(),name='otpvalidate'),
    path('otp/resend/',OTPResend.as_view(),name='otpresend')
]


urlpatterns = format_suffix_patterns(urlpatterns)