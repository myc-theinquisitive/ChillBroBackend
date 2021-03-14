# API's

### Get All Addresses
url: http://127.0.0.1:8000/address/
method: GET

input data: None

output data:
[
    {
        "id": 1,
        "name": "123",
        "phone_number": "9998887766",
        "pincode": "54321",
        "address_line": "line 1",
        "extend_address": null,
        "landmark": "landmark",
        "city": "VSKP",
        "state": "AP",
        "country": "IND",
        "latitude": "1.1",
        "longitude": "1.1"
    },
]


### Get Address by id
url: http://127.0.0.1:8000/address/1/
method: GET

input data: None

output data:
{
    "id": 1,
    "name": "123",
    "phone_number": "9998887766",
    "pincode": "54321",
    "address_line": "line 1",
    "extend_address": null,
    "landmark": "landmark",
    "city": "VSKP",
    "state": "AP",
    "country": "IND",
    "latitude": "1.1",
    "longitude": "1.1"
}


### Create Address
url: http://127.0.0.1:8000/address/
method: POST

input data:
{
    "name": "123",
    "phone_number": "9998887766",
    "pincode": "54321",
    "address_line": "line 1",
    "extend_address": null,
    "landmark": "landmark",
    "city": "VSKP",
    "state": "AP",
    "country": "IND",
    "latitude": "1.1",
    "longitude": "1.1"
}

output data: object instance


### Update Address
url: http://127.0.0.1:8000/address/1/
method: PUT

input data: same as create

output data: object instance


### Get Address By Ids
url: http://127.0.0.1:8000/address/get_by_ids/
method: GET

input data:
{
    "ids": [1, 2]
}

output data:
[
    {
        "id": 1,
        "name": "123",
        "phone_number": "9998887766",
        "pincode": "54321",
        "address_line": "line 1",
        "extend_address": null,
        "landmark": "landmark",
        "city": "VSKP",
        "state": "AP",
        "country": "IND",
        "latitude": "1.1",
        "longitude": "1.1"
    },
    {
        "id": 2,
        "name": "Bharat",
        "phone_number": "9998887766",
        "pincode": "55555",
        "address_line": "line 2",
        "extend_address": null,
        "landmark": "landmark",
        "city": "VSKP",
        "state": "AP",
        "country": "IND",
        "latitude": "1",
        "longitude": "1"
    }
]
