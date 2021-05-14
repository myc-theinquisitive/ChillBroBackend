import firebase_admin
from firebase_admin import credentials, messaging

# cred = credentials.Certificate("ChillBro/Notifications/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

def sendPush(title, msg, registration_token, dataObject = None):
    pass
