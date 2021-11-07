from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .wrapper import *
from .conversions import *
from .validations import *


def add_products_to_cart(products, product_id, quantity, size, cart, product_details, transport_details, event_details):
    is_combo = product_details[product_id]["is_combo"]
    has_sub_products = product_details[product_id]["has_sub_products"]
    cart_product_serializer = CartProductsSerializer()
    all_sizes = size
    cart_product_id = None
    if len(all_sizes) == 0:
        cart_product_id = cart_product_serializer.create(
            {
                "cart": cart,
                "product_id": product_id,
                "quantity": quantity,
                "size": None,
                "is_combo": is_combo,
                "hidden": False,
                "has_sub_products": has_sub_products,
                "parent_cart_product": None
            }
        )
    else:
        cart_product_sizes = []
        for each_size in all_sizes:
            cart_product_sizes.append(
                {
                    "cart": cart,
                    "product_id": product_id,
                    "quantity": all_sizes[each_size],
                    "size": each_size,
                    "is_combo": is_combo,
                    "hidden": False,
                    "has_sub_products": has_sub_products,
                    "parent_cart_product": None
                }
            )
        cart_product_serializer.bulk_create(cart_product_sizes)

    if cart_product_id is not None:
        # TODO: Instead of checking length specify allow null and allow blank for serializer
        if len(transport_details) > 0:
            cart_product_extra_details_serializer = TransportDetailsSerializer()
            cart_product_extra_details_serializer.create(
                {
                    "cart_product": cart_product_id,
                    "trip_type": transport_details["trip_type"],
                    "pickup_location": post_create_address(transport_details['pickup_location'])["address_id"],
                    "drop_location": post_create_address(transport_details['drop_location'])["address_id"]
                }
            )
        if len(event_details) > 0:
            events_details_serializer = EventsDetailsSerializer()
            price_details = event_details.pop("prices", None)
            event_details["cart_product"] = cart_product_id
            event_details_object = events_details_serializer.create(event_details)

            for each_price in price_details:
                each_price["event_details"] = event_details_object

            events_prices_serializer = EventsPricesSerializer()
            events_prices_serializer.bulk_create(price_details)

        if is_combo or has_sub_products:
            combo_cart_products = []
            for each_combo_product in products:
                combo_cart_products.append(
                    {
                        "cart": cart,
                        "product_id": each_combo_product['product_id'],
                        "quantity": each_combo_product['quantity'],
                        "size": each_combo_product['size'],
                        "is_combo": False,
                        "hidden": True,
                        "parent_cart_product": cart_product_id
                    }
                )
            cart_product_serializer.bulk_create(combo_cart_products)

    return True


def check_availability_of_product(new_product_details, user_id):
    required_objects = defaultdict()
    product_id = new_product_details['product_id']
    quantity = new_product_details['quantity']
    size = convert_sizes_list_to_dict(new_product_details['sizes'])
    combo_product_details = convert_combo_products_list_to_dict_of_dictionaries(
        new_product_details['combo_product_details'])
    transport_details = event_details = {}
    if "transport_details" in new_product_details:
        transport_details = new_product_details['transport_details']
    if "event_details" in new_product_details:
        event_details = new_product_details['event_details']

    entity_id, entity_type = check_valid_product(product_id)
    if entity_id is None and entity_type is None:
        return False, "Invalid Product"
    required_objects["entity_id"] = entity_id
    required_objects["entity_type"] = entity_type

    product_ids = [product_id]
    product_details = get_product_id_wise_product_details(product_ids)

    required_objects["product_details"] = product_details
    required_objects["product_id"] = product_id
    required_objects["quantity"] = quantity
    required_objects["size"] = size
    required_objects["transport_details"] = transport_details
    required_objects["event_details"] = event_details

    is_valid, errors = is_product_valid(product_details, product_id, quantity, size, combo_product_details)
    if not is_valid:
        return is_valid, errors

    is_valid, errors = check_valid_duration([product_id], new_product_details['start_time'], \
                                            new_product_details['end_time'])
    if not is_valid:
        return is_valid, errors

    if entity_type == EntityType.TRANSPORT.value:
        if transport_details['km_limit_choosen'] > 0:
            if transport_details['km_limit_choosen'] not in \
                    product_details[product_id]['transport_details']['price_details']:
                return False, "Invalid km limit choosen"

        is_valid, errors = check_valid_address(transport_details['pickup_location'])
        if not is_valid:
            return is_valid, errors
        is_valid, errors = check_valid_address(transport_details['drop_location'])
        if not is_valid:
            return is_valid, errors

    if entity_type == EntityType.EVENT.value:
        product_event_details = product_details[product_id]["event_details"]

        if product_event_details["start_time"] > new_product_details["start_time"] or \
                product_event_details["end_time"] < new_product_details["end_time"]:
            return False, "Invalid event date"
        price_details = convert_list_of_dict_to_dict_of_dict(product_event_details["price_classes"],"price")
        for each_price in event_details["prices"]:
            if each_price["price"] not in price_details:
                return False, "Invalid price {}".format(each_price["price"])
            if each_price["quantity"] > product_details[product_id]["quantity"]:
                return False, "Maximum quantity is {}".format(product_details[product_id]["quantity"])

        slot_details = convert_list_of_dict_to_dict_of_dict(product_event_details["slots"],"name")
        if event_details["slot"] not in slot_details:
            return False, "Invalid slot {}".format(event_details["slot"])

    all_product_ids, products = combine_all_products(product_id, size, quantity, \
                                                     combo_product_details, product_details)
    required_objects["products"] = products

    cart = None
    try:
        cart = Cart.objects.get(entity_id=entity_id, entity_type=entity_type, \
                                start_time=new_product_details['start_time'], \
                                end_time=new_product_details['end_time'], created_by=user_id)
        is_cart_exist = True
    except ObjectDoesNotExist:
        is_cart_exist = False
    required_objects["is_cart_exist"] = is_cart_exist

    if not is_cart_exist:
        is_valid, errors = check_valid_booking(products, new_product_details['start_time'], \
                                               new_product_details['end_time'])
    else:
        cart_products = CartProducts.objects.filter(cart=cart, product_id__in=all_product_ids)
        all_cart_products = []

        for each_product in cart_products:
            if each_product.product_id == product_id and each_product.parent_cart_product_id is None:
                return False, "Product already exists in cart"

            if not each_product.is_combo and not each_product.has_sub_products:
                all_cart_products.append(
                    {
                        "product_id": each_product.product_id,
                        "quantity": each_product.quantity,
                        "size": each_product.size
                    }
                )
        all_cart_products += products
        is_valid, errors = check_valid_booking(combine_products(all_cart_products), \
                                               new_product_details['start_time'], \
                                               new_product_details['end_time'])

    if is_valid:
        return is_valid, required_objects
    return is_valid, errors


class CheckAvailability(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddProductToCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)

        is_valid, required_objects = check_availability_of_product(request.data, request.user)

        if not is_valid:
            return Response({"message": "Product not available!!", "errors": required_objects}, 400)
        return Response({"message": "Product is available"}, 200)


class AddProductToCart(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
            {
                "product_id":"b45e3f28-87da-48ce-aaed-49102108e696",
                "quantity":1,
                "sizes":[],
                "combo_product_details":[
                    {
                        "product_id":"48675d13-a700-4593-ac09-f5063ceaa386",
                        "sizes":[
                            {
                                "size":"",
                                "quantity":1
                            }
                        ]
                    },
                    {
                        "product_id":"af8524ad-47a7-469b-9066-294ea315f65b",
                        "sizes":[
                            {
                                "size":"L",
                                "quantity":1
                            },
                            {
                                "size":"XS",
                                "quantity":1
                            }
                        ]
                    },
                    {
                        "product_id":"fdf090e0-ca32-4b27-8bfe-d37d4818334e",
                        "sizes":[
                            {
                                "size":"XS",
                                "quantity":2
                            }
                        ]
                    }
                ],
                "start_time":"2021-10-29T00:00:00",
                "end_time":"2021-10-30T15:00:00",
                "is_transport": false,
                "transport_details": {
                    "trip_type":"SINGLE",
                    "km_limit_choosen": 0,
                    "pickup_location": {
                        "name": null,
                        "phone_number": null,
                        "pincode": "533122",
                        "address_line": null,
                        "extend_address": null,
                        "landmark": null,
                        "city": "VSKP",
                        "state": "AP",
                        "country": "IND",
                        "latitude": null,
                        "longitude": null
                    },
                    "drop_location":{
                        "name": null,
                        "phone_number": null,
                        "pincode": "533122",
                        "address_line": null,
                        "extend_address": null,
                        "landmark": null,
                        "city": "VSKP",
                        "state": "AP",
                        "country": "IND",
                        "latitude": null,
                        "longitude": null
                    }
                }
            }
        """

        input_serializer = AddProductToCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)

        is_valid, required_objects = check_availability_of_product(request.data, request.user)
        if not is_valid:
            return Response({"message": "Can't add product to cart", "errors": required_objects}, 400)

        if not required_objects["is_cart_exist"]:
            serializer = CartSerializer()
            cart = serializer.create(
                {
                    'entity_id': required_objects["entity_id"],
                    'entity_type': required_objects["entity_type"],
                    'start_time': request.data['start_time'],
                    'end_time': request.data['end_time'],
                    'created_by': request.user
                }
            )
        else:
            cart = Cart.objects.get(entity_id=required_objects["entity_id"], \
                                    entity_type=required_objects["entity_type"], \
                                    start_time=request.data['start_time'], \
                                    end_time=request.data['end_time'], created_by=request.user)

        add_products_to_cart(required_objects["products"], required_objects["product_id"], required_objects["quantity"], \
                             required_objects["size"], cart, required_objects["product_details"], \
                             required_objects["transport_details"], required_objects['event_details'])

        return Response({"message": "Product added to cart successfully", "cart_id": cart.id}, 200)


class AddMultipleBookings(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddMultipleBookingsSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response({"message":"Can't create multiple bookings", "errors": input_serializer.errors},400)
        start_time = request.data["start_time"]
        end_time = request.data["end_time"]
        overall_is_valid = True
        errors = defaultdict()
        added = defaultdict()
        products = request.data["products"]
        for each_product in products:
            each_product["start_time"] = start_time
            each_product["end_time"] = end_time
            is_valid, required_objects = check_availability_of_product(each_product, request.user)
            if not is_valid:
                overall_is_valid = False
                errors[each_product["product_id"]] = required_objects
            else:
                if not required_objects["is_cart_exist"] :
                    serializer = CartSerializer()
                    cart = serializer.create(
                        {
                            'entity_id': required_objects["entity_id"],
                            'entity_type': required_objects["entity_type"],
                            'start_time': request.data['start_time'],
                            'end_time': request.data['end_time'],
                            'created_by': request.user
                        }
                    )
                else:
                    cart = Cart.objects.get(entity_id=required_objects["entity_id"], \
                                            entity_type=required_objects["entity_type"], \
                                            start_time=request.data['start_time'], \
                                            end_time=request.data['end_time'], created_by=request.user)

                add_products_to_cart(required_objects["products"], required_objects["product_id"],
                                     required_objects["quantity"], \
                                     required_objects["size"], cart, required_objects["product_details"], \
                                     required_objects["transport_details"], required_objects['event_details'])
                added[each_product["product_id"]] = "Successfully added"
        if not overall_is_valid:
            return Response({"message":"Can't create multiple bookings", "errors": errors,"added":added},400)

        return Response({"message": "Successfully Booking Created", "added":added}, 200)

