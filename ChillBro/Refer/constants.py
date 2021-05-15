import enum

SHARE_APP_MESSAGE = '''CHILLBRO CONNECT!
        A new business model for increasing Your revenue 💰 in any kind of Trips
        We recommend you to download the CHILLBRO CONNECT app here.
        Link: https://www.chillbro.co.in'''

class SignUpRequestStatus(enum.Enum):
    YET_TO_VERIFY = "YET_TO_VERIFY"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"