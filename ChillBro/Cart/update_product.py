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


class UpdateCartProduct(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        """
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
        """
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

