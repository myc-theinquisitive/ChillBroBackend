#API's

###Get Discount
url : http://127.0.0.1:8000/coupons/discount/
method: POST

input data: 
{
    "coupon_code": "NEWCOUPON",
    "entity_ids": ["1"],
    "product_ids": ["1"],
    "order_value": 500
}

output data:
{
    "new_price": 300
}


###Use Coupon
url: http://127.0.0.1:8000/coupons/use_coupon/
method: POST

input data:
{
    "coupon_code": "NEWCOUPON",
    "entity_ids": ["1"],
    "product_ids": ["1"],
    "order_id": "6",
    "order_value": 500
}

output data:
{
    "message": "You saved 200"
}


###Get All Coupons
url: http://127.0.0.1:8000/coupons/
method: GET

input data: None

output data:
[
    {
        "id": 15,
        "discount": {
            "id": 48,
            "value": 100,
            "is_percentage": true,
            "max_value_if_percentage": 200
        },
        "ruleset": {
            "id": 28,
            "allowed_users": {
                "id": 46,
                "users": [],
                "all_users": true
            },
            "allowed_entities": {
                "id": 33,
                "entities": [],
                "all_entities": true
            },
            "allowed_products": {
                "id": 31,
                "products": [],
                "all_products": true
            },
            "max_uses": {
                "id": 34,
                "max_uses": 100,
                "is_infinite": false,
                "uses_per_user": 50
            },
            "validity": {
                "id": 31,
                "start_date": "2021-01-01T00:00:00",
                "end_date": "2021-12-31T00:00:00",
                "is_active": true,
                "minimum_order_value": 100
            }
        },
        "code": "NEWCOUPON",
        "title": null,
        "description": null,
        "terms_and_conditions": null,
        "times_used": 1,
        "created": "2021-03-11T15:07:54.124710"
    }
]


###Get Single Coupon
url: http://127.0.0.1:8000/coupons/1/
method: POST

input data: None

output data: Single coupon details


###Create coupon
url: http://127.0.0.1:8000/coupons/
method: POST

input data:
{
    "code": "NEWCOUPON4",
    "title": "Title",
    "description": "Description",
    "terms_and_conditions": [
        "TC1",
        "TC2"
    ],
    "discount" : {
        "value": 100,
        "is_percentage": true,
        "max_value_if_percentage": 200
    },
    "ruleset" : {
        "allowed_users" : {
            "users" : ["1", "2"],
            "all_users" : false
        },
        "allowed_entities" : {
            "entities" : [],
            "all_entities" : true
        },
        "allowed_products" : {
            "products" : [],
            "all_products" : true
        },
        "max_uses" : {
            "max_uses" : 100,
            "is_infinite" : false,
            "uses_per_user" : 50
        },
        "validity" : {
            "start_date": "2021-01-01T00:00:00",
            "end_date": "2021-12-31T00:00:00",
            "is_active" : true,
            "minimum_order_value" : 100
        }
    }
}

output data: coupon details


###Update Coupon
url: http://127.0.0.1:8000/coupons/1/
method: PUT

input data: Same as create

output data: coupon details


###Get Coupon History
url: http://127.0.0.1:8000/coupons/history/
method: GET

input data: 
{
    "coupon_code": "NEWCOUPON"
}

output data:
[
    {
        "id": 14,
        "discount": {
            "id": 53,
            "value": 100,
            "is_percentage": true,
            "max_value_if_percentage": 200
        },
        "ruleset": {
            "id": 33,
            "allowed_users": {
                "id": 51,
                "users": [],
                "all_users": true
            },
            "allowed_entities": {
                "id": 38,
                "entities": [],
                "all_entities": true
            },
            "allowed_products": {
                "id": 36,
                "products": [],
                "all_products": true
            },
            "max_uses": {
                "id": 39,
                "max_uses": 100,
                "is_infinite": false,
                "uses_per_user": 50
            },
            "validity": {
                "id": 36,
                "start_date": "2021-01-01T00:00:00",
                "end_date": "2021-12-31T00:00:00",
                "is_active": true,
                "minimum_order_value": 100
            }
        },
        "code": "NEWCOUPON",
        "title": null,
        "description": null,
        "terms_and_conditions": null,
        "times_used": 0,
        "created": "2021-03-11T15:11:31.962587",
        "changed_by": 1
    }
]


###Get Available coupons
url: http://127.0.0.1:8000/coupons/available/
method: POST

input data:
{
    "entity_ids": ["1"],
    "product_ids": ["1"],
    "order_value": 100
}

output data:
[
    {
        "coupon_code": "NEWCOUPON",
        "title": null,
        "description": null,
        "terms_and_conditions": null,
        "available": true,
        "reason": ""
    },
    {
        "coupon_code": "NEWCOUPON2",
        "title": "Title",
        "description": null,
        "terms_and_conditions": [
            "TC1",
            "TC2"
        ],
        "available": true,
        "reason": ""
    },
    {
        "coupon_code": "NEWCOUPON3",
        "title": "Title",
        "description": "Description",
        "terms_and_conditions": [
            "TC1",
            "TC2"
        ],
        "available": true,
        "reason": ""
    },
    {
        "coupon_code": "NEWCOUPON4",
        "title": "Title",
        "description": "Description",
        "terms_and_conditions": [
            "TC1",
            "TC2"
        ],
        "available": true,
        "reason": ""
    }
]
