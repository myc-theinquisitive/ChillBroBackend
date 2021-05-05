
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("C:/Users/surya/PycharmProjects/ChillBroBackend/ChillBro/Notifications/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


def sendPush(title, msg, registration_token, dataObject = None):
    message = messaging.MulticastMessage(
        notification = messaging.Notification(
            title = title,
            body = msg,
            image = "http://chillbro.co.in/static/assets/images/CHILLBRO.jpeg"
        ),
        data = dataObject,
        tokens = registration_token,
    )

    response = messaging.send_multicast(message)
    return True


