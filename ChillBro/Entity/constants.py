import enum


class Status(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class EntityTypes(enum.Enum):
    Hotel = "Hotel"
    Transport = "Transport"
    Rental = "Rental"

class Cities(enum.Enum):
   VSKP = "VISAKHAPATNAM"

SHARE_APP_MESSAGE = '''
        CHILLBRO CONNECT!
        A new business model for increasing Your revenue 💰 in any kind of Trips
        We recommend you to download the CHILLBRO CONNECT app here.
        Link: https://www.chillbro.co.in
    '''