import enum

class NotificationType(enum.Enum):
    BOOKINGS = "BOOKINGS"
    PAYMENTS = "PAYMENTS"
    GENERAL = "GENERAL"
    APPROVALS = "APPROVALS"

class NotificationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

setting = {
    "all": True,
    "bookings": True,
    "payments": True,
    "general": True
}