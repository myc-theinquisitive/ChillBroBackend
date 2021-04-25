from rest_framework.authtoken.models import Token
from rest_framework import authentication
from rest_framework import exceptions
import jwt
from django.conf import settings


class JWTAuthentication(authentication.BaseAuthentication):
    
    def authenticate(self, request):
        if "token" not in request.COOKIES:
            return None

        try:
            encoded_token = request.COOKIES['token']
            token_dict = jwt.decode(encoded_token, settings.SECRET_KEY, algorithms=["HS256"])
            token = token_dict["token"]
            token_object = Token.objects.get(key=token)
        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid Token')
        
        return token_object.user, None
