import enum


class Departments(enum.Enum):
    CUSTOMER_CARE = "CUSTOMER_CARE"
    FINANCE = "FINANCE"


def getProducts():
    products = ['1', '2', '3']
    return products


def getOrders():
    orders = ['1', '2', '3']
    return orders
