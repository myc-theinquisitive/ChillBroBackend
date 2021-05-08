import enum


class EntityType(enum.Enum):
    hotels = "HOTELS"
    transport = "TRANSPORT"
    rentals = "RENTALS"
    resorts = "RESORTS"
    events = "EVENTS"


class FeedbackCategory(enum.Enum):
    suggestion = "SUGGESTION"
    something_is_not_quite_right = "SOMETHING IS NOT QUITE RIGHT"
    compliment = "COMPLIMENT"
