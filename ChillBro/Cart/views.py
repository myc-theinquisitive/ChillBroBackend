from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .wrapper import check_valid_booking, get_product_details_with_image, check_valid_product, \
    get_product_id_wise_product_details, get_discounted_value, create_multiple_bookings_from_cart, \
    post_create_address, check_valid_duration, get_product_price_values, update_address_details, \
    check_valid_address
from .helpers import get_date_format
from collections import defaultdict
from .constants import ProductTypes


# TODO: Describe all the inputs to the functions, if dictionary specify all the keys in it


def is_product_valid(product_details, product_id, quantity, all_sizes, combo_product_details):
    is_valid = True
    errors = defaultdict(list)
    if quantity < 1:
        is_valid = False
        errors[product_id].append("Quantity must be greater than zero")

    if product_details[product_id]['has_sizes']:
        product_sizes_details = product_details[product_id]['size_products']
        if len(all_sizes) == 0 and len(product_sizes_details) > 0:
            is_valid = False
            errors[product_id].append("Please choose sizes")
        else:
            total_quantity = 0
            for each_size in all_sizes:
                try:
                    # for validation of size - if the size selected by user is valid for this product or not
                    products_quantity = product_sizes_details[each_size]
                    total_quantity += all_sizes[each_size]
                except KeyError:
                    is_valid = False
                    errors[product_id].append("Invalid Size")
            if total_quantity != quantity:
                is_valid = False
                errors[product_id].append("Please select sizes for all quantity - {}".format(quantity))

    if product_details[product_id]["is_combo"]:
        combo_products_data = product_details[product_id]['combo_products']
        if len(combo_products_data) != len(combo_product_details):
            is_valid = False
            errors[product_id].append("Invalid combo product data")

        # combo sub products sizes will be checked in booking validation
        # TODO: Better to validate sizes here as well  --- booking validation means checking in adding cart only sir
        for each_combo_product in combo_product_details:
            try:
                product_quantity = combo_products_data[each_combo_product]['quantity']
                combo_product_size_details = combo_product_details[each_combo_product]
                total_product_quantity = 0
                for each_size in combo_product_size_details:
                    total_product_quantity += combo_product_size_details[each_size]

                if len(combo_product_size_details) > 0 and \
                        product_quantity * quantity != total_product_quantity:
                    is_valid = False
                    errors[product_id].append("{} product should have {} sizes"
                                              .format(each_combo_product, product_quantity * quantity))
            except KeyError:
                is_valid = False
                errors[product_id].append("Invalid combo product data")

    return is_valid, errors


def combine_all_products(product_id, size, quantity, combo_product_details, product_details):
    products = []
    all_product_ids = [product_id]
    if product_details[product_id]["is_combo"]:
        combo_products_data = product_details[product_id]['combo_products']
        for each_combo_product in combo_products_data:
            all_product_ids.append(each_combo_product)
            all_sizes = combo_product_details[each_combo_product]

            if len(all_sizes) == 0:
                products.append(
                    {
                        "product_id": each_combo_product,
                        "quantity": combo_product_details[each_combo_product]['quantity'] * quantity,
                        "size": None,
                        "parent_booked_product": product_id
                    }
                )
            else:
                for each_size in all_sizes:
                    products.append(
                        {
                            "product_id": each_combo_product,
                            "quantity": all_sizes[each_size],
                            "size": each_size,
                            "parent_booked_product": product_id
                        }
                    )

    elif product_details[product_id]["has_sub_products"]:
        sub_products = product_details[product_id]["sub_products"]
        for each_sub_product in sub_products:
            all_product_ids.append(each_sub_product)
            sub_product_sizes = sub_products[each_sub_product]['size']
            if len(sub_product_sizes) == 0:
                sub_product_size = None
                products.append(
                    {
                        "product_id": each_sub_product,
                        "quantity": sub_products[each_sub_product]['quantity'] * quantity,
                        "size": sub_product_size,
                        "parent_booked_product": product_id
                    }
                )
            else:
                # this case is not there at present
                for each_size in sub_product_sizes:
                    products.append(
                        {
                            "product_id": each_sub_product,
                            "quantity": sub_product_sizes[each_size] * quantity,
                            "size": each_size,
                            "parent_booked_product": product_id
                        }
                    )
    else:
        all_sizes = size
        if len(all_sizes) == 0:
            products.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "size": None,
                    "parent_booked_product": None
                }
            )
        for each_size in all_sizes:
            products.append(
                {
                    "product_id": product_id,
                    "quantity": all_sizes[each_size],
                    "size": each_size,
                    "parent_booked_product": None
                }
            )

    return all_product_ids, products


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

    # TODO: This condition specifies that product with sizes does not have sub products or combo products.
    #  need to validate this
    if cart_product_id is not None:
        # TODO: Instead of checking length specify allow null and allow blank for serializer and
        #  add is_transport boolean variable to identify - specify its default value as false
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


def convert_combo_products_list_to_dict_of_dictionaries(list_of_combo_products):
    dict_of_combo_products = defaultdict()
    for each_combo_product in list_of_combo_products:
        dict_of_sizes = defaultdict()
        for each_size in each_combo_product['sizes']:
            dict_of_sizes[each_size['size']] = each_size['quantity']
        dict_of_combo_products[each_combo_product['product_id']] = dict_of_sizes

    return dict_of_combo_products


def convert_sizes_list_to_dict(list_of_sizes):
    dict_of_sizes = defaultdict()
    for each_size in list_of_sizes:
        dict_of_sizes[each_size['size']] = each_size['quantity']

    return dict_of_sizes


def check_availability_of_product(new_product_details, user_id):
    required_objects = defaultdict()
    product_id = new_product_details['product_id']
    quantity = new_product_details['quantity']
    size = convert_sizes_list_to_dict(new_product_details['sizes'])
    combo_product_details = convert_combo_products_list_to_dict_of_dictionaries(
        new_product_details['combo_product_details'])
    transport_details = new_product_details['transport_details']
    event_details = new_product_details['event_details']

    entity_id, entity_type = check_valid_product(product_id)
    if entity_id is None and entity_type is None:
        return False, "Invalid Product"
    required_objects["entity_id"] = entity_id
    required_objects["entity_type"] = entity_type

    product_ids = [product_id]
    product_details = get_product_id_wise_product_details(product_ids)

    # return True, product_details
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

    # if entity_type == "TRANSPORT":    #Uncomment this whenever top level category names as TRANSPORT only
    if len(transport_details) > 0:
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

    if entity_type == "EVENT":
        product_event_details = product_details[product_id]["event_details"]

        if product_event_details["start_time"] > event_details["date"] or \
                product_event_details["end_time"] < event_details["date"]:
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


def convert_list_of_dict_to_dict_of_dict(list_of_dict, unique_id):
    dict_of_dict = defaultdict()
    for each_dict in list_of_dict:
        dict_of_dict[each_dict[unique_id]] = each_dict

    return dict_of_dict


class CheckAvailability(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddProductToCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)

        is_valid, required_objects = \
            check_availability_of_product(request.data, request.user)

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

        # TODO: add all the fields passed in request to the serializer for validation
        input_serializer = AddProductToCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)

        is_valid, required_objects = check_availability_of_product(request.data, request.user)
        # return Response(required_objects)
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


class UpdateCartProduct(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO: Use serializer for validating the data and move all validations to a separate function
    def put(self, request, *args, **kwargs):
        '''
        {
            "cart": "e639c85b-1a51-49f4-8109-3e8328d71170",
            "product_id": "9935c1ec-d940-4927-a3cd-ec3c2ad2b40b",
            "quantity": 1,
            "sizes": [],
            "combo_product_details": [
            ],
            "start_time": "2021-10-28T00:00:00",
            "end_time": "2021-10-29T15:00:00",
            "is_transport": false,
            "transport_details": {
                "trip_type":"SINGLE",
                "km_limit_choosen": 0,
                "is_pickup_location_updated" :true,
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
                "is_drop_location_updated": true,
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
        '''
        start_time = request.data['start_time']
        end_time = request.data['end_time']
        product_id = request.data['product_id']
        quantity = request.data['quantity']
        size = convert_sizes_list_to_dict(request.data['sizes'])

        product_details = get_product_id_wise_product_details([product_id])
        combo_product_details = convert_combo_products_list_to_dict_of_dictionaries(
            request.data['combo_product_details'])
        cart_products = CartProducts.objects.select_related('cart').filter(cart=request.data['cart'])
        if len(cart_products) == 0:
            return Response({"message": "Can't update the product quantity",
                             "errors": "invalid cart id or product id"}, 400)

        is_valid, errors = is_product_valid(product_details, product_id, quantity, size, combo_product_details)
        if not is_valid:
            return Response({"message": "Can't add product to cart", "errors": errors})

        # For finding the actual product that is to be updated
        cart_product = None
        for each_cart_product in cart_products:
            if each_cart_product.parent_cart_product is None and each_cart_product.product_id == product_id:
                cart_product = each_cart_product
                break

        # If trying to update hidden product
        if cart_product is None:
            return Response({"message": "Can't update the product quantity",
                             "errors": "invalid cart id or product id"}, 400)

        all_product_ids, products = combine_all_products(product_id, size, quantity, combo_product_details,
                                                         product_details)

        cart_products = CartProducts.objects.filter(cart=request.data['cart'], product_id__in=all_product_ids)
        all_cart_products = []
        for each_product in cart_products:
            if each_product.product_id == product_id and each_product.parent_cart_product_id is None:
                continue
            if not each_product.is_combo and not each_product.has_sub_products and \
                    each_product.parent_cart_product != cart_product:
                all_cart_products.append({
                    "product_id": each_product.product_id,
                    "quantity": each_product.quantity,
                    "size": each_product.size
                })
        all_cart_products += products

        is_valid, errors = check_valid_booking(combine_products(all_cart_products), start_time, end_time)
        if not is_valid:
            return Response({"message": "Can't update the product quantity", "errors": errors}, 400)

        try:
            new_cart = Cart.objects.get(entity_id=cart_product.cart.entity_id, \
                                        entity_type=cart_product.cart.entity_type, \
                                        start_time=request.data['start_time'], \
                                        end_time=request.data['end_time'], created_by=request.user)
        except ObjectDoesNotExist:
            cart_serializer = CartSerializer()
            new_cart = cart_serializer.create({'entity_id': cart_product.cart.entity_id, \
                                               'entity_type': cart_product.cart.entity_type, \
                                               'start_time': request.data['start_time'], \
                                               'end_time': request.data['end_time'], 'created_by': request.user})

        is_product_with_sizes = 0
        if product_details[product_id]["is_combo"]:
            combo_details = product_details[product_id]["combo_products"]
            for each_product in combo_details:
                if len(combo_details[each_product]['sizes']) > 0:
                    is_product_with_sizes = 1

        elif product_details[product_id]["has_sub_products"]:
            sub_products_details = product_details[product_id]["sub_products"]
            for each_product in sub_products_details:
                if len(sub_products_details[each_product]['size']) > 0:
                    is_product_with_sizes = 1
        elif product_details[product_id]['has_sizes']:
            is_product_with_sizes = 1
        else:
            cart_product.quantity = quantity
            cart_product.save()

        cart_product = CartProducts.objects \
            .filter(cart=request.data['cart'], product_id=product_id, parent_cart_product=None)
        cart = cart_product[0].cart
        cart_product = cart_product[0]

        if request.data['is_transport']:
            transport_details = request.data["transport_details"]
        else:
            transport_details = {}
        if is_product_with_sizes == 1:
            cart_product.delete()
            add_products_to_cart(products, product_id, quantity, size, cart, product_details, transport_details, {})
        else:
            cart_products = CartProducts.objects.filter(Q(cart=request.data['cart']) & Q(Q(product_id=product_id) |
                                                                                         Q(
                                                                                             parent_cart_product=cart_product)))

            update_cart_products = []
            for each_product in cart_products:
                sub_products_details = defaultdict()
                if product_details[product_id]["is_combo"]:
                    sub_products_details = product_details[product_id]["combo_products"]
                elif product_details[product_id]["has_sub_products"]:
                    sub_products_details = product_details[product_id]["sub_products"]
                if each_product.parent_cart_product is None:
                    update_cart_products.append({"id": each_product.id, "cart": new_cart, \
                                                 "quantity": quantity, "size": None})
                else:
                    update_cart_products.append(
                        {
                            "id": each_product.id,
                            "cart": new_cart,
                            "quantity": quantity * sub_products_details[each_product.product_id]['quantity'],
                            "size": None
                        }
                    )
            bulk_update_serializer = CartProductsSerializer()
            bulk_update_serializer.bulk_update(update_cart_products)

            if request.data['is_transport']:
                previous_transport_data = TransportDetails.objects.get(cart_product=cart_product)
                if transport_details['is_pickup_location_updated']:
                    update_address_details(previous_transport_data.pickup_location,
                                           transport_details['pickup_location'])
                if transport_details['is_drop_location_updated']:
                    update_address_details(previous_transport_data.drop_location, transport_details['drop_location'])
                previous_transport_data.trip_type = transport_details['trip_type']
                previous_transport_data.km_limit_choosen = transport_details['km_limit_choosen']
                previous_transport_data.save()

        return Response(
            {"message": "Product Quantity is updated to {} and size is updated to {}".format(quantity, size)}, 200)


class CartDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        cart_id_wise_product_details = []
        if kwargs['entity_type'] == 'ALL':
            total_carts_products = CartProducts.objects.select_related('cart').filter(cart__created_by=request.user)
        else:
            total_carts_products = CartProducts.objects.select_related('cart').filter(cart__created_by=request.user, \
                                                                                      cart__entity_type=kwargs[
                                                                                          'entity_type'])
        if len(total_carts_products) == 0:
            return Response({"message": "Sorry, There are no carts"}, 200)

        product_ids = []
        for each_product in total_carts_products:
            product_ids.append(each_product.product_id)
        product_id_wise_product_details = get_product_details_with_image(product_ids)

        cart_products_after_removing_duplicate_products = []

        sizes_combination_for_all_products = defaultdict(list)
        quantity_for_all_products = defaultdict()
        for each_cart_product in total_carts_products:
            if len(sizes_combination_for_all_products[
                       each_cart_product.cart_id + "," + each_cart_product.product_id + "," + \
                       str(each_cart_product.hidden)]) == 0:
                cart_products_after_removing_duplicate_products.append(each_cart_product)
                quantity_for_all_products[each_cart_product.cart_id + "," + each_cart_product.product_id + "," + \
                                          str(each_cart_product.hidden)] = 0
            if (each_cart_product.size == "" or each_cart_product.size == None):
                pass
            else:
                sizes_combination_for_all_products[
                    each_cart_product.cart_id + "," + each_cart_product.product_id + "," + \
                    str(each_cart_product.hidden)].append({
                    "quantity": each_cart_product.quantity,
                    "size": each_cart_product.size
                })

            quantity_for_all_products[each_cart_product.cart_id + "," + each_cart_product.product_id + "," + \
                                      str(each_cart_product.hidden)] = quantity_for_all_products[
                                                                           each_cart_product.cart_id + "," + \
                                                                           each_cart_product.product_id + "," + str(
                                                                               each_cart_product.hidden)] + each_cart_product.quantity;

        sub_products_details = defaultdict(list)
        for each_cart_product in cart_products_after_removing_duplicate_products:
            each_product_details = product_id_wise_product_details[each_cart_product.product_id]
            each_product_details.pop('featured', None)
            each_product_details.pop('features', None)
            each_product_details.pop('seller', None)
            each_product_details.pop('rating', None)
            if each_cart_product.hidden:
                sub_product_cart_details = {
                    "selected_details": {
                        "combo_quantity": quantity_for_all_products[each_cart_product.cart_id + "," + \
                                                                    each_cart_product.product_id + "," + str(
                            each_cart_product.hidden)],
                        "sizes": sizes_combination_for_all_products[each_cart_product.cart_id + "," + \
                                                                    each_cart_product.product_id + "," + str(
                            each_cart_product.hidden)]
                    }
                }
                sub_product_cart_details.update(each_product_details)
                sub_products_details[
                    each_cart_product.cart_id + "," + each_cart_product.parent_cart_product.product_id].append(
                    sub_product_cart_details)

        for each_product in cart_products_after_removing_duplicate_products:
            sub_products = []
            if each_product.hidden is False:
                each_product_details = product_id_wise_product_details[each_product.product_id]
                each_product_details.pop('featured', None)
                each_product_details.pop('features', None)
                each_product_details.pop('seller', None)
                each_product_details.pop('rating', None)
                if each_product.is_combo or each_product.has_sub_products:
                    sub_products = sub_products_details[each_product.cart_id + "," + each_product.product_id]

                cart_product_details = {
                    "selected_details": {
                        'id': each_product.id,
                        'quantity': quantity_for_all_products[each_product.cart_id + "," + \
                                                              each_product.product_id + "," + str(each_product.hidden)],
                        'size': sizes_combination_for_all_products[each_product.cart_id + "," + \
                                                                   each_product.product_id + "," + str(
                            each_product.hidden)],
                        'start_time': each_product.cart.start_time,
                        'end_time': each_product.cart.end_time,
                        'sub_products': sub_products
                    }
                }
                cart_product_details.update(each_product_details)
                cart_id_wise_product_details.append(cart_product_details)

        return Response({"results": cart_id_wise_product_details}, 200)


class DeleteProductFromCart(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CartProducts.objects.all()
    serializer_class = CartProductsSerializer


class DeleteCart(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CheckAvailabilityOfAllProducts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if kwargs['entity_type'] == "ALL":
            all_cart_products = CartProducts.objects.select_related('cart') \
                .filter(cart__created_by=request.user)
        else:
            all_cart_products = CartProducts.objects.select_related('cart') \
                .filter(cart__created_by=request.user, cart__entity_type=kwargs['entity_type'])
        out_of_stock_products = defaultdict(list)

        sub_products_details = defaultdict(list)
        for each_cart_product in all_cart_products:
            if each_cart_product.hidden:
                sub_products_details[
                    each_cart_product.cart_id + "," + each_cart_product.parent_cart_product.product_id].append(
                    {
                        "product_id": each_cart_product.product_id,
                        "quantity": each_cart_product.quantity,
                        "size": each_cart_product.size,
                    }
                )

        for each_product in all_cart_products:
            products = []
            if each_product.hidden is False:
                if each_product.is_combo:
                    products = sub_products_details[each_product.cart_id + "," + each_product.product_id]
                else:
                    products.append(
                        {
                            "product_id": each_product.product_id,
                            "quantity": each_product.quantity,
                            "size": each_product.size
                        }
                    )

                is_valid, errors = check_valid_booking(
                    products,
                    each_product.cart.start_time.strftime(get_date_format()),
                    each_product.cart.end_time.strftime(get_date_format())
                )
                if not is_valid:
                    out_of_stock_products[each_product.cart.id].append({each_product.product_id: errors})
        return Response(out_of_stock_products, 200)


class CheckoutCart(ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = CheckoutCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Cant checkout the cart", "errors": input_serializer.errors}, 400)

        cart_details = Cart.objects.filter(created_by=request.user, entity_type=request.data['entity_type'])
        cart_items = CartProducts.objects.select_related('cart') \
            .filter(cart__created_by=request.user, cart__entity_type=request.data['entity_type'])

        if len(cart_details) == 0:
            return Response({"message": "Can't checkout", "errors": "Sorry, no products in cart"})

        entity_ids = []
        for each_cart in cart_details:
            entity_ids.append(each_cart.entity_id)

        cart_product_ids = []
        product_ids = []
        for each_product in cart_items:
            product_ids.append(each_product.product_id)
            cart_product_ids.append(each_product.id)
        product_details = get_product_id_wise_product_details(product_ids)

        transport_details = TransportDetails.objects.filter(cart_product_id__in=cart_product_ids)
        all_cart_products_transport_details = defaultdict()
        for each_cart_product in transport_details:
            all_cart_products_transport_details[each_cart_product.cart_product.product_id] = each_cart_product

        total_products_value, product_price_values = \
            calculate_total_products_value(cart_items, product_details, all_cart_products_transport_details)

        coupon = request.data['coupon']
        total_coupon_value = 0

        if len(request.data['coupon']) > 0:
            coupon_data = get_discounted_value(
                coupon, request.user, product_ids, entity_ids, request.data['entity_type'], total_products_value)
            if not coupon_data['is_valid']:
                return Response({"message": "Can't create the booking", "errors": coupon['errors']}, 400)
            total_coupon_value = total_products_value - coupon_data['discounted_value']

        cart_products_for_bookings = form_each_cart_all_products(cart_items, all_cart_products_transport_details,
                                                                 product_price_values, product_details,
                                                                 total_products_value, total_coupon_value)

        final_cart_details = defaultdict()
        for each_cart in cart_details:
            final_cart_details[each_cart.id] = {
                "coupon": coupon,
                "created_by": request.user,
                "entity_id": each_cart.entity_id,
                "entity_type": each_cart.entity_type,
                "start_time": each_cart.start_time.strftime(get_date_format()),
                "end_time": each_cart.end_time.strftime(get_date_format()),
                "products": cart_products_for_bookings[each_cart.id],
            }
        final_cart_details['all_product_details'] = product_details

        is_valid, errors = create_multiple_bookings_from_cart(final_cart_details)

        if is_valid:
            cart_details.delete()
            return Response({"message": "Successfully created {} bookings".format(len(final_cart_details))})
        else:
            return Response({"message": "Can't create bookings", "errors": errors})


def calculate_coupon_value(total_coupon_value, product_value, total_products_value, quantity):
    return (float(total_coupon_value) / 100) * \
           ((float(product_value) / float(total_products_value)) * 100) * quantity


def combine_products(all_cart_products):
    form_together = defaultdict()
    for each_product in all_cart_products:
        if each_product['size'] is None:
            size = ""
        else:
            size = each_product['size']
        try:
            form_together[each_product['product_id'] + "," + size] = {
                "product_id": each_product['product_id'],
                "quantity": form_together[each_product['product_id'] + "," + size]['quantity']
                            + each_product['quantity'],
                "size": each_product['size']
            }
        except KeyError:
            form_together[each_product['product_id'] + "," + size] = {
                "product_id": each_product['product_id'],
                "quantity": each_product['quantity'],
                "size": each_product['size']
            }
    final_products = []
    for each_product in form_together:
        final_products.append(form_together[each_product])

    return final_products


def form_each_cart_all_products(cart_items, transport_details, product_price_values,
                                product_details, total_products_value, total_coupon_value):
    cart_products_for_bookings = defaultdict(list)
    for each_cart_product in cart_items:
        if each_cart_product.hidden:
            cart_products_for_bookings[each_cart_product.cart_id].append(
                {
                    "product_id": each_cart_product.product_id,
                    "quantity": each_cart_product.quantity,
                    "size": each_cart_product.size,
                    "parent_booked_product": each_cart_product.parent_cart_product.product_id,
                    "coupon_value": 0,
                    "product_value": 0,
                    "is_combo": False,
                    "has_sub_products": False,
                    "transport_details": {}
                }
            )
        else:
            coupon_value_for_each_product = 0
            if total_coupon_value > 0:
                coupon_value_for_each_product = calculate_coupon_value(
                    total_coupon_value, product_details[each_cart_product.product_id]['price'],
                    total_products_value, each_cart_product.quantity)

            transport_data = get_transport_data(each_cart_product.product_id, product_details, transport_details)

            cart_products_for_bookings[each_cart_product.cart_id].append({
                "product_id": each_cart_product.product_id,
                "quantity": each_cart_product.quantity,
                "size": each_cart_product.size,
                "parent_booked_product": None,
                "coupon_value": coupon_value_for_each_product,
                "product_value": product_price_values[each_cart_product.product_id]["discounted_price"],
                "is_combo": each_cart_product.is_combo,
                "has_sub_products": each_cart_product.has_sub_products,
                "transport_details": {
                    "trip_type": transport_data["trip_type"],
                    "pickup_location": transport_data["pickup_location"],
                    "drop_location": transport_data["drop_location"],
                    "km_limit_choosen": transport_data["km_limit_choosen"]
                }
            })

    return cart_products_for_bookings


def calculate_total_products_value(cart_products, product_details, transport_details):
    group_product_details_by_type = defaultdict(dict)
    group_product_ids_by_type = defaultdict(list)

    for each_cart_product in cart_products:
        if not each_cart_product.hidden:
            product_type = product_details[each_cart_product.product_id]['type']

            transport_data = get_transport_data(each_cart_product.product_id, product_details, transport_details)

            group_product_ids_by_type[product_type].append(each_cart_product.product_id)
            group_product_details_by_type[product_type].update(
                {
                    each_cart_product.product_id: {
                        "quantity": each_cart_product.quantity,
                        "size": each_cart_product.size,
                        "start_time": each_cart_product.cart.start_time,
                        "end_time": each_cart_product.cart.end_time,
                        "trip_type": transport_data["trip_type"],
                        "discount_percentage": product_details[each_cart_product.product_id]["discount"],
                        "km_limit_choosen": transport_data["km_limit_choosen"]
                    }
                }
            )

    product_price_values = get_product_price_values(group_product_ids_by_type, group_product_details_by_type)

    total_products_value = 0
    for each_product in cart_products:
        if not each_product.hidden:
            total_products_value += product_price_values[each_product.product_id]['discounted_price']

    return total_products_value, product_price_values


def get_transport_data(product_id, product_details, transport_details):
    product_type = product_details[product_id]['type']

    if product_id in transport_details:
        transport_data = {
            "trip_type": transport_details[product_id].trip_type,
            "pickup_location": transport_details[product_id].pickup_location,
            "drop_location": transport_details[product_id].drop_location,
            "km_limit_choosen": transport_details[product_id].km_limit_choosen
        }
    else:
        transport_data = {
            "trip_type": "",
            "pickup_location": "",
            "drop_location": "",
            "km_limit_choosen": 0
        }

    return transport_data
