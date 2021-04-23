# API's

### Get All Issues
url: http://127.0.0.1:8000/issues/
method: GET

input data: None

output data:
[
    {
        "id": 1,
        "user_id": "2",
        "current_department": "CUSTOMER_CARE",
        "current_employeeId": null,
        "issue_title": "first issue",
        "description": "check whether workng or not",
        "entity": "hi",
        "order_id": "1",
        "product_id": "2",
        "status": "TODO",
        "final_resolution": null,
        "created_at": "2021-04-10T20:29:42.673198",
        "updated_at": null
    }
]


### Get Issue by id
url: http://127.0.0.1:8000/issues/7/
method: GET

input data: None

output data:
{
    "id": 7,
    "user_id": "6",
    "current_department": "CUSTOMER_CARE",
    "current_employeeId": null,
    "issue_title": "my title",
    "description": "naade",
    "entity": "tourism",
    "order_id": "2",
    "product_id": "3",
    "status": "TODO",
    "final_resolution": null,
    "created_at": "2021-04-12T08:31:10.504473",
    "updated_at": "2021-04-12T08:31:10.504744"
}


### Create Issue
url: http://127.0.0.1:8000/issues/
method: POST

input data:
{
    "issue_title":"APP is very slow",
    "description":"Developers should work more.",
    "entity":"Travels",
    "order_id":"1a2bc3",
    "product_id":"7y3j2w"
}

output data: 
{
    "message": "Issue inserted successfully",
    "issue id": 10
}


### Update Issue
url: http://127.0.0.1:8000/address/1/
method: PUT

input data: same as create

output data: object instance

### Delete Issues
url: http://127.0.0.1:8000/issues/7/

input data: None

output data: None

### Close Issue by employee
url: http://127.0.0.1:8000/issues/close/
method: PUT

input data:
{
    "issue_id":10,
    "final_resolution":"every thing is fine, app will work fine now",
    "current_employeeId":"123"
}

output data:
{
    "id": 10,
    "status": "DONE",
    "current_employeeId": "123",
    "final_resolution": "every thing is fine, app will work fine now"
}

### Pick issue by employee
url: http://127.0.0.1:8000/issues/pick/
method: PUT
input data:
{
    "issue_id":2,
    "current_employeeId":"123"
}

output data:
{
    "id": 2,
    "status": "IN_PROGRESS",
    "current_employeeId": "123",
    "final_resolution": "Issue is not yet resolved"
}

### Close issue by user
url: http://127.0.0.1:8000/issues/close/user/
method: PUT

input data:
{
    "issue_id":2
}

output data:
{
    "final_resolution": "Issue closed by user",
    "status": "DONE",
    "user_id": "6",
    "current_employeeId": null
}

### Department, Status filtered Issues
url: http://127.0.0.1:8000/issues/CUSTOMER_CARE/TODO/
method: Get

input data: None

output data: 
[
    {
        "id": 1,
        "user_id": "2",
        "current_department": "CUSTOMER_CARE",
        "current_employeeId": null,
        "issue_title": "first issue",
        "description": "check whether workng or not",
        "entity": "hi",
        "order_id": "1",
        "product_id": "2",
        "status": "TODO",
        "final_resolution": null,
        "created_at": "2021-04-10T20:29:42.673198",
        "updated_at": null
    },
    {
        "id": 5,
        "user_id": "6",
        "current_department": "CUSTOMER_CARE",
        "current_employeeId": null,
        "issue_title": "my title",
        "description": "naade",
        "entity": "tourism",
        "order_id": "2",
        "product_id": "3",
        "status": "TODO",
        "final_resolution": null,
        "created_at": "2021-04-12T08:29:39.330278",
        "updated_at": "2021-04-12T08:29:39.330850"
    }
]

url: http://127.0.0.1:8000/issues/CUSTOMER_CARE/IN_PROGRESS/
input data:
none

output data:[]

### Transfer issue to other department
url: http://127.0.0.1:8000/issues/transfer/
method: POST

input data:
{
    "employee_id":"123",
    "employee_comment":"finance issue will take care",
    "transferred_to":"FINANCE",
    "issue_id":"10"
}

output data:
{
    "id": 6,
    "employee_id": "123",
    "employee_comment": "finance issue will take care",
    "created_at": "2021-04-13T18:40:01.310021",
    "transferred_to": "FINANCE",
    "issue_id": 10
}

### Transfer History of Issues
url: http://127.0.0.1:8000/issues/transfer-history/2
method: Get

input data:
None

Output data:
[
    {
        "id": 1,
        "employee_id": "2",
        "employee_comment": "please clear this issue",
        "created_at": "2021-04-10T21:07:53.454051",
        "transferred_to": "FINANCE",
        "issue_id": 2
    },
    {
        "id": 3,
        "employee_id": "2",
        "employee_comment": "nice one",
        "created_at": "2021-04-12T22:54:21.357148",
        "transferred_to": "FINANCE",
        "issue_id": 2
    }
]