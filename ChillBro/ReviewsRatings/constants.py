import enum


REVIEW_SCALE = 5


class EntityType(enum.Enum):
    hotels = "HOTEL"
    transport = "TRANSPORT"
    rentals = "RENTAL"
    events = "EVENT"


class FeedbackCategory(enum.Enum):
    suggestion = "SUGGESTION"
    something_is_not_quite_right = "SOMETHING IS NOT QUITE RIGHT"
    compliment = "COMPLIMENT"
