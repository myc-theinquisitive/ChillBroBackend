from django.db.models import Q
from .helpers import get_date_format
from .add_product import *
from .update_product import *


def checkout_cart(coupon, entity_type, user):
    cart_details = Cart.objects.filter(created_by=user, entity_type=entity_type)
    cart_items = CartProducts.objects.select_related('cart') \
        .filter(cart__created_by=user, cart__entity_type=entity_type)

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

    event_detail_objects = EventsDetails.objects.filter(cart_product_id__in=cart_product_ids)
    event_detail_ids = []
    for each_event_detail in event_detail_objects:
        event_detail_ids.append(each_event_detail.id)
    event_price_details_objects = EventsPrices.objects.filter(event_details_id__in=event_detail_ids)
    event_price_details = defaultdict(list)
    for each_event_price in event_price_details_objects:
        event_price_details[each_event_price.event_details_id].append({"price":each_event_price.price, \
                                                                       "quantity": each_event_price.quantity})

    all_cart_products_event_details = defaultdict()
    for each_cart_product in event_detail_objects:
        each_cart_product.prices = event_price_details[each_cart_product.id]
        all_cart_products_event_details[each_cart_product.cart_product.product_id] = each_cart_product

    total_products_value, product_price_values = \
        calculate_total_products_value(cart_items, product_details, all_cart_products_transport_details,\
                                       all_cart_products_event_details)

    total_coupon_value = 0

    if len(coupon) > 0:
        coupon_data = get_discounted_value(
            coupon, user, product_ids, entity_ids, entity_type, total_products_value)
        if not coupon_data['is_valid']:
            return Response({"message": "Can't create the booking", "errors": coupon['errors']}, 400)
        total_coupon_value = total_products_value - coupon_data['discounted_value']

    cart_products_for_bookings = form_each_cart_all_products(cart_items, all_cart_products_transport_details,
                                    all_cart_products_event_details,product_price_values, product_details,
                                    total_products_value, total_coupon_value)

    final_cart_details = defaultdict()
    for each_cart in cart_details:
        final_cart_details[each_cart.id] = {
            "coupon": coupon,
            "created_by": user,
            "entity_id": each_cart.entity_id,
            "entity_type": each_cart.entity_type,
            "start_time": each_cart.start_time.strftime(get_date_format()),
            "end_time": each_cart.end_time.strftime(get_date_format()),
            "products": cart_products_for_bookings[each_cart.id],
        }
    final_cart_details['all_product_details'] = product_details

    is_valid, errors = create_multiple_bookings_from_cart(final_cart_details)
    total_bookings = 0
    if is_valid:
        cart_details.delete()
        total_bookings = len(final_cart_details)

    return is_valid, errors, total_bookings


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
                                        each_cart_product.product_id + "," + str(each_cart_product.hidden)],
                        "sizes": sizes_combination_for_all_products[each_cart_product.cart_id + "," + \
                                        each_cart_product.product_id + "," + str(each_cart_product.hidden)]
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
        entity_type = request.data["entity_type"]
        coupon = request.data['coupon']
        is_valid, errors, total_bookings = checkout_cart(coupon, entity_type, request.user)

        if is_valid:
            return Response({"message": "Successfully created {} bookings".format(total_bookings)})
        else:
            return Response({"message": "Can't create bookings", "errors": errors})
