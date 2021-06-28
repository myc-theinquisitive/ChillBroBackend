import enum


class Department(enum.Enum):
    HR = "HR"
    CUSTOMER_CARE = "CUSTOMER_CARE"
    MARKETING = "MARKETING"
    LEGAL = "LEGAL"


class AttendanceStatus(enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class LeaveStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
