# API's

### Get All Categories
url : http://127.0.0.1:8000/category/
method: GET

input data: None

output data:
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Rentals",
            "description": "Products for rent charged per time",
            "parent_category": null
        },
    ]
}


### Create Category
url : http://127.0.0.1:8000/category/
method: POST

input data: 
{
    "name": "Camera",
    "description": "Camera for better photos",
    "parent_category" : 1
}


output data: Category details


### Get Category
url: http://127.0.0.1:8000/category/1/
method: GET

input data: None

output data:
{
    "id": 1,
    "name": "Rentals",
    "description": "Products for rent charged per time",
    "parent_category": null
}


### Update Category
url: http://127.0.0.1:8000/category/1/
method: PUT

input data:
{
    "name": "Rentals",
    "description": "Products (Camera, Tent, Bike) for rent charged per time",
    "parent_category": null
}

output data: category details


### Delete Category
url: http://127.0.0.1:8000/category/1/
method: DELETE

input data: None

output data: None


### Create Category Image
url: http://127.0.0.1:8000/category/image/
method: POST

input data:
{
    "category": 1,
    "image": file,
    "order": 0
}

output data: Category Image Details


### Delete Category Image
url: http://127.0.0.1:8000/category/image/1/
method: DELETE

input data: None

output data: None


### Get ALL Categories Level wise
url: http://127.0.0.1:8000/category/level_wise/
method: GET

input data: None

output data:
[
    {
        "id": 1,
        "name": "Rentals",
        "description": "Products (Camera, Tent, Bike) for rent charged per time",
        "sub_categories": [
            {
                "id": 2,
                "name": "Camera",
                "description": "Camera for better photos",
                "sub_categories": [],
                "images": [
                    {
                        "id": 2,
                        "image": "http://127.0.0.1:8000/static/images/Category/camera/camera-a7c709f5-56ab-41a1-80cd-900fc50f819e.jpeg",
                        "order": 2
                    }
                ]
            }
        ],
        "images": [
            {
                "id": 3,
                "image": "http://127.0.0.1:8000/static/images/Category/rentals/rentals-ab1f4c95-b0d7-48a7-885b-ab67711a6ff5.jpeg",
                "order": 1
            },
            {
                "id": 4,
                "image": "http://127.0.0.1:8000/static/images/Category/rentals/rentals-8ed2d151-0e74-4658-8a0d-eca6a626e0b3.jpeg",
                "order": 2
            },
            {
                "id": 5,
                "image": "http://127.0.0.1:8000/static/images/Category/rentals/rentals-254a7ecd-ac37-4f9e-a8a8-a7bd1579e39c.jpeg",
                "order": 3
            }
        ]
    }
]


### Get Level wise categories for given category
url: http://127.0.0.1:8000/category/level_wise/category_name/
method: GET

input data: None

output data:
{
    "id": 1,
    "name": "Rentals",
    "description": "Products (Camera, Tent, Bike) for rent charged per time",
    "sub_categories": [
        {
            "id": 2,
            "name": "Camera",
            "description": "Camera for better photos",
            "sub_categories": [],
            "images": [
                {
                    "id": 2,
                    "image": "http://127.0.0.1:8000/static/images/Category/camera/camera-a7c709f5-56ab-41a1-80cd-900fc50f819e.jpeg",
                    "order": 2
                }
            ]
        }
    ],
    "images": [
        {
            "id": 3,
            "image": "http://127.0.0.1:8000/static/images/Category/rentals/rentals-ab1f4c95-b0d7-48a7-885b-ab67711a6ff5.jpeg",
            "order": 1
        },
        {
            "id": 4,
            "image": "http://127.0.0.1:8000/static/images/Category/rentals/rentals-8ed2d151-0e74-4658-8a0d-eca6a626e0b3.jpeg",
            "order": 2
        },
        {
            "id": 5,
            "image": "http://127.0.0.1:8000/static/images/Category/rentals/rentals-254a7ecd-ac37-4f9e-a8a8-a7bd1579e39c.jpeg",
            "order": 3
        }
    ]
}


### Create Product
url: http://127.0.0.1:8000/product/
method: POST

input data:
{
    "name": "Hotel JJ New Single Room 1",
    "description": "Single Room",
    "type": "Hotel",
    "price": "19000.00",
    "category": 2,
    "discounted_price": "17000.00",
    "hotel_room": {
        "amenities": [
            {
                "amenity": 1,
                "is_available": true
            }
        ]
    }
}

output data: Product details


### Get Product
url: http://127.0.0.1:8000/product/product_url/
method: GET

input data: None
output data: same as get product by ids


### Update Product
url: http://127.0.0.1:8000/product/product_url/
method: PUT

input data:
{
    "name": "Hotel JJ New Single Room 2",
    "description": "Single Room in Hotel JJ",
    "type": "Hotel",
    "category": 2,
    "price": "10000.00",
    "discounted_price": "7000.00",
    "hotel_room": {
        "amenities": {
            "add": [
                {
                    "amenity": string,
                    "is_available": boolean
                }
            ]
            "change": [
                {
                    "id": string,
                    "is_available": boolean
                }
            ]
            "delete": [
                {
                    "id": string
                }
            ]
        }
    }
}

output data: Product details


### Create Product Image
url: http://127.0.0.1:8000/product/image/
method: POST

input data:
{
    "product": 1,
    "image": file,
    "order": 0
}

output data: Product Image Details


### Delete Product Image
url: http://127.0.0.1:8000/product/image/1/
method: DELETE

input data: None

output data: None


### Get All Product Amenities
url: http://127.0.0.1:8000/product/amenities/
method: GET

input data: None

output data:
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "AC"
        },
        {
            "id": 2,
            "name": "TV"
        },
        {
            "id": 3,
            "name": "Refrigirator"
        }
    ]
}


### Create Product Amenity
url: http://127.0.0.1:8000/hotel/amenities/
method: POST

input data:
{
    "name": "Refrigirator"
}

output data: Amenity details


### Get Product by ids - of different types:
url: http://127.0.0.1:8000/product/
method: GET

input data:
{
    "ids": [1]
}

output data:
[
    {
        "id": 1,
        "name": "Hotel JJ New Single Room 1",
        "description": "Single Room",
        "type": "Hotel",
        "price": "19000.00",
        "discounted_price": "17000.00",
        "featured": false,
        "active": true,
        "category": 2,
        "url": "product/hotel-jj-new-single-room-1",
        "images": [
            {
                "id": 4,
                "image": "http://127.0.0.1:8000/static/images/Product/hotel-jj-new-single-room-1/hotel-jj-new-single-room-1-5941988d-d4_i2MpREx.jpeg",
                "order": 0
            },
            {
                "id": 5,
                "image": "http://127.0.0.1:8000/static/images/Product/hotel-jj-new-single-room-1/hotel-jj-new-single-room-1-6bb4a98c-77_hGzr13H.jpeg",
                "order": 1
            }
        ],
        "hotel_room": {
            "id": 1,
            "available_amenities": [
                {
                    "id": 1,
                    "name": "AC",
                    "is_available": true
                }
            ]
        }
    }
]


### Get Product By Category
url: http://127.0.0.1:8000/product/category/category_name/
method: GET

input data: None

output data:
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Hotel JJ New Single Room 1",
            "description": "Single Room",
            "type": "Hotel",
            "price": "19000.00",
            "discounted_price": "17000.00",
            "featured": false,
            "active": true,
            "category": 2,
            "url": "product/hotel-jj-new-single-room-1",
            "images": [
                {
                    "id": 4,
                    "image": "http://127.0.0.1:8000/static/images/Product/hotel-jj-new-single-room-1/hotel-jj-new-single-room-1-5941988d-d4_i2MpREx.jpeg",
                    "order": 0
                },
                {
                    "id": 5,
                    "image": "http://127.0.0.1:8000/static/images/Product/hotel-jj-new-single-room-1/hotel-jj-new-single-room-1-6bb4a98c-77_hGzr13H.jpeg",
                    "order": 1
                }
            ],
            "hotel_room": {
                "id": 1,
                "available_amenities": [
                    {
                        "id": 1,
                        "name": "AC",
                        "is_available": true
                    }
                ]
            }
        }
    ]
}
