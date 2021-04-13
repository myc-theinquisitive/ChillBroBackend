# ChillBroBackend
Backend functionality for Chill Bro app

## Installation

### Install virtualenv
pip install virtualenv

### Create venv
python -m venv .venv

### Activate venv
cd .venv/Scripts
activate

### Install requirements
pip install -r requirements.txt



#API's 


#POST -- localhost:8000/bookings/

Input:
{
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "products":[{"product_id":"df8966f9-f6ce-4a46-9a00-80ac3988f818","entity_id":"df8966f9-f6ce-4a46-9a00-80ac3988f818","start_time":"2021-03-25T11:07:00","end_time":"2021-03-26T11:07:00","quantity":4},{"product_id":"df8966f9-f6ce-4a46-9a00-80ac3988f819","entity_id":"df8966f9-f6ce-4a46-9a00-80ac3988f818","start_time":"2021-03-28T11:07:00","end_time":"2021-03-30T11:07:00","quantity":12},{"product_id":"df8966f9-f6ce-4a46-9a00-80ac3988f820","entity_id":"df8966f9-f6ce-4a46-9a00-80ac3988f818","start_time":"2021-04-08T12:07:00","end_time":"2021-04-12T14:07:00","quantity":2}],
            "entity_type": "RESORTS",
            "payment_status": "DONE"
}

Output: 
Success

#GET -- localhost:8000/bookings/

Input - None

Output:
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T16:01:20",
            "total_money": "500.00",
            "entity_type": "HOTELS",
            "booking_status": "ONGOING",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "64845d73-79b5-4159-a2b0-ebdfa37ec12a",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T16:49:50.847722",
            "total_money": "500.00",
            "entity_type": "RENTALS",
            "booking_status": "PENDING",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "7831eef0-cdee-4fa7-9fc5-49f65617ea47",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T17:05:05",
            "total_money": "500.00",
            "entity_type": "RESORTS",
            "booking_status": "CANCELLED",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "fb97e520-d37b-429f-8b27-3763b7b3ddd4",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T17:27:52.868560",
            "total_money": "1500.00",
            "entity_type": "RESORTS",
            "booking_status": "PENDING",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "c12b33b8-00da-4004-a66d-8fa86d78bef2",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T17:37:25.997297",
            "total_money": "1500.00",
            "entity_type": "RESORTS",
            "booking_status": "PENDING",
            "payment_status": "DONE",
            "user": 1
        }
    ]
}




#GET - localhost:8000/bookings/orderedproducts

Input: 
{
    "booking_id":"1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca"
}

Output:
[
    {
        "id": 1,
        "product_id": "df8966f9-f6ce-4a46-9a00-80ac3988f818",
        "entity_id": "",
        "start_time": "2021-03-25T11:07:00",
        "end_time": "2021-03-26T11:07:00",
        "quantity": 1,
        "product_value": "100.00",
        "is_cancelled": false,
        "product_status": "PENDING",
        "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca"
    },
    {
        "id": 2,
        "product_id": "df8966f9-f6ce-4a46-9a00-80ac3988f819",
        "entity_id": "",
        "start_time": "2021-03-28T11:07:00",
        "end_time": "2021-03-30T11:07:00",
        "quantity": 1,
        "product_value": "200.00",
        "is_cancelled": false,
        "product_status": "PENDING",
        "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca"
    },
    {
        "id": 3,
        "product_id": "df8966f9-f6ce-4a46-9a00-80ac3988f820",
        "entity_id": "",
        "start_time": "2021-04-08T12:07:00",
        "end_time": "2021-04-12T14:07:00",
        "quantity": 1,
        "product_value": "300.00",
        "is_cancelled": false,
        "product_status": "PENDING",
        "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca"
    }
]


#PUT - localhost:8000/bookings/cancelorder
Input:
{
    "booking_id":"1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca"
}

Output:
{
    "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca",
    "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
    "booking_date": "2021-04-13T16:01:20.816455",
    "total_money": "500.00",
    "entity_type": "Rentals",
    "booking_status": "CANCELLED",
    "payment_status": "DONE",
    "user": 1
}


#GET -localhost:8000/bookings/orderdetails

Input:
{
    "booking_filter":"Today", // Today, Yesterday, Week, Month
    "entity_filter": "",      //HOTELS, TRANSPORT, RENTALS, RESORTS, EVENTS
    "status" : []             // PENDING, ONGOING, CANCELLED, DONE
}


Output:
[
    {
        "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca",
        "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
        "booking_date": "2021-04-13T16:01:20",
        "total_money": "500.00",
        "entity_type": "HOTELS",
        "booking_status": "ONGOING",
        "payment_status": "DONE",
        "user": 1
    },
    {
        "booking_id": "64845d73-79b5-4159-a2b0-ebdfa37ec12a",
        "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
        "booking_date": "2021-04-13T16:49:50.847722",
        "total_money": "500.00",
        "entity_type": "RENTALS",
        "booking_status": "PENDING",
        "payment_status": "DONE",
        "user": 1
    },
    {
        "booking_id": "7831eef0-cdee-4fa7-9fc5-49f65617ea47",
        "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
        "booking_date": "2021-04-13T17:05:05",
        "total_money": "500.00",
        "entity_type": "RESORTS",
        "booking_status": "CANCELLED",
        "payment_status": "DONE",
        "user": 1
    },
    {
        "booking_id": "fb97e520-d37b-429f-8b27-3763b7b3ddd4",
        "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
        "booking_date": "2021-04-13T17:27:52.868560",
        "total_money": "1500.00",
        "entity_type": "RESORTS",
        "booking_status": "PENDING",
        "payment_status": "DONE",
        "user": 1
    },
    {
        "booking_id": "c12b33b8-00da-4004-a66d-8fa86d78bef2",
        "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
        "booking_date": "2021-04-13T17:37:25.997297",
        "total_money": "1500.00",
        "entity_type": "RESORTS",
        "booking_status": "PENDING",
        "payment_status": "DONE",
        "user": 1
    }
]



#GET - localhost:8000/bookings/statistics

Input :
{
    "booking_filter":"Today", // Today, Yesterday, Week, Month
    "entity_filter": "HOTELS" //HOTELS, TRANSPORT, RENTALS, RESORTS, EVENTS
}

Output:
ongoing : 1
cancelled : 0
pending : 0


#GET - localhost:8000/bookings/userorders

Input- None

Output:

{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "booking_id": "1e3c5d13-1b9c-40fe-88cc-f3dbc3eab4ca",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T16:01:20",
            "total_money": "500.00",
            "entity_type": "HOTELS",
            "booking_status": "ONGOING",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "64845d73-79b5-4159-a2b0-ebdfa37ec12a",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T16:49:50.847722",
            "total_money": "500.00",
            "entity_type": "RENTALS",
            "booking_status": "PENDING",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "7831eef0-cdee-4fa7-9fc5-49f65617ea47",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T17:05:05",
            "total_money": "500.00",
            "entity_type": "RESORTS",
            "booking_status": "CANCELLED",
            "payment_status": "DONE",
            "user": 1
        },
        {
            "booking_id": "fb97e520-d37b-429f-8b27-3763b7b3ddd4",
            "coupon": "df8966f9-f6ce-4a46-9a00-80ac3988f822",
            "booking_date": "2021-04-13T17:27:52.868560",
            "total_money": "1500.00",
            "entity_type": "RESORTS",
            "booking_status": "PENDING",
            "payment_status": "DONE",
            "user": 1
        }
    ]
}