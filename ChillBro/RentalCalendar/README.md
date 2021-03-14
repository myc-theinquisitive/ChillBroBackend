# API's

### Create Rent Booking
url: http://127.0.0.1:8000/rental_calendar/
method: POST

input data:
{
    "booking_id": "11",
    "product_id": "1",
    "product_quantity": 2,
    "start_time": "2021-03-03T23:00:00",
    "end_time": "2021-03-04T00:00:00",
    "is_cancelled": "False"
}

output data:
{
    "message": "Booking Created"
}


### Update Rent Booking
url: http://127.0.0.1:8000/rental_calendar/
method: PUT

input data:
{
    "product_id": "1",
    "product_quantity": 2,
    "start_time": "2021-03-03T00:00:00",
    "end_time": "2021-03-03T05:00:00",
    "booking_id": "5",
    "is_cancelled": false
}

output data:
{
    "message": "Booking Updated"
}


### Get All Booking
url: http://127.0.0.1:8000/rental_calendar/get_all/
method: GET

input data: None

output data:
[
    {
        "product_id": "1",
        "start_time": "2021-03-03T00:00:00",
        "end_time": "2021-03-03T01:00:00",
        "booking_id": "3",
        "is_cancelled": true
    },
]


### Cancel Booking
url: http://127.0.0.1:8000/rental_calendar/cancel_booking/
method: POST

input data: 
{
    "product_id": "1",
    "booking_id": "3"
}

output data:
{
    "message": "Booking Cancelled"
}


### Product Availability
url: http://127.0.0.1:8000/rental_calendar/product_availability/
method: POST

input data:
{
    "product_id": "1",
    "product_quantity": 2,
    "start_time": "2021-03-03T00:00:00",
    "end_time": "2021-03-03T05:00:00"
}

output data:
{
    "availabilities": [
        {
            "start_hour": "2021-03-03T00:00:00",
            "end_hour": "2021-03-03T01:00:00",
            "available_count": 1
        },
        {
            "start_hour": "2021-03-03T01:00:00",
            "end_hour": "2021-03-03T02:00:00",
            "available_count": 0
        },
        {
            "start_hour": "2021-03-03T02:00:00",
            "end_hour": "2021-03-03T03:00:00",
            "available_count": 1
        },
        {
            "start_hour": "2021-03-03T03:00:00",
            "end_hour": "2021-03-03T04:00:00",
            "available_count": 0
        },
        {
            "start_hour": "2021-03-03T04:00:00",
            "end_hour": "2021-03-03T05:00:00",
            "available_count": 0
        }
    ]
}


### Product Booking
url: http://127.0.0.1:8000/rental_calendar/product/bookings/
method: POST

input data:
{
    "product_id": "1",
    "start_time": "2021-03-03T00:00:00",
    "end_time": "2021-03-04T00:00:00"
}

output data:
[
    {
        "product_id": "1",
        "start_time": "2021-03-03T00:00:00",
        "end_time": "2021-03-03T01:30:00",
        "booking_id": "4",
        "is_cancelled": false
    },
]


### Cancelled Product Bookings
url: http://127.0.0.1:8000/rental_calendar/product/cancelled_bookings/
method: POST

input data:
{
    "product_id": "1",
    "start_time": "2021-03-03T00:00:00",
    "end_time": "2021-03-04T00:00:00"
}

output data:
[
    {
        "product_id": "1",
        "start_time": "2021-03-03T00:00:00",
        "end_time": "2021-03-03T01:00:00",
        "booking_id": "3",
        "is_cancelled": true
    }
]
