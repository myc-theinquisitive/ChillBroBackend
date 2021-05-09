from django.conf import settings

def get_user_model():
    return settings.AUTH_USER_MODEL
