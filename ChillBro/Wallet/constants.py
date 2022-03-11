import enum


class TransactionType(enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class RewardType(enum.Enum):
    BOOKING = "BOOKING"
    REFER_AND_EARN = "REFER_AND_EARN"
