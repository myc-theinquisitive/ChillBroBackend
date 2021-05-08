import requests
from requests.cookies import RequestsCookieJar

cookie = RequestsCookieJar()


def login():
    data = {
        "email": "suryavamsi66666@gmail.com",
        "password":"password"
    }
    url = 'http://127.0.0.1:8000/auth/login/'
    response = requests.post(url, data=data)
    global cookie
    cookie = response.cookies
    print(response.text)


def IsAuthenticated():
    if(len(cookie)==0):
        return False
    return True


def createBusinessClient():
    if not IsAuthenticated():
        return "Access denied"
    data = {
        "first_name":"new one",
        "email":"vamsi@gmail.com",
        "password":"Vamsi@12345",
        "phone_number":"7893444336",
        "business_name":"vamsi business",
        "secondary_contact":"7899877898"
    }
    url = 'http://127.0.0.1:8000/user/business_client/'
    response = requests.post(url, data=data, cookies=cookie)
    print(response.text)





login()
createBusinessClient()
# CreateBooking()

def CreateBooking():
    if not IsAuthenticated():
        return "Access denied"
    data ={
            "coupon": "NEWCOUPON",
            "products":[{"product_id":"df8966f9-f6ce-4a46-9a00-80ac3988f818","quantity":2}],
            "entity_type": "RESORTS",
            "payment_status": "DONE",
            "entity_id":"df8966f9-f6ce-4a46-9a00-80ac3988f819",
            "start_time":"2021-04-30T11:07:00",
            "end_time":"2021-05-30T11:07:00"
    }
    url = 'http://127.0.0.1:8000/bookings/'
    response = requests.post(url, data=data, cookies= cookie)
    print(response.text)