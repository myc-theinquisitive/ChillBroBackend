import json
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum, Count
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .booking_calendar_helper import product_availability_per_hour
from .booking_helper import cancel_booking, update_booking_status, get_complete_booking_details_by_ids, \
    get_check_in_details
from .serializers import *
from .helpers import *
from .constants import *
from collections import defaultdict
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsOwner, IsEmployee, IsBookingBusinessClient, \
    IsBookingEmployee, IsBusinessClientEntities, IsEmployeeEntities
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from .validators import validate_booking_product_availability, validate_start_end_time, validate_booking_product_details, \
    validate_booking_details
from .wrapper import get_product_id_wise_product_details, create_refund_transaction, \
    update_booking_transaction_in_payment, create_booking_transaction, get_transaction_details_by_booking_id, \
    business_client_review_on_customer, get_product_details, get_entity_details, is_product_valid, \
    get_business_client_review_by_booking_id, get_product_prices_by_duration, get_product_net_price, \
    check_valid_duration, check_valid_address, combine_all_products, entity_id_and_entity_type, get_coupon_value, \
    get_product_price_values, post_create_address, booking_id_wise_reward_points_earned, \
    get_booking_id_product_id_wise_ratings
from .wrapper import get_product_id_wise_basic_details
import copy


# Lock for creating a new booking or updating the booking timings
_booking_lock = threading.Lock()


class GetProductAvailability(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ProductAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        product_id = serializer.data["product_id"]
        start_time = serializer.data["start_time"]
        end_time = serializer.data["end_time"]
        product_size = serializer.data["product_size"]

        return product_availability_per_hour(
            product_id=product_id, start_time=start_time, end_time=end_time, product_size=product_size)


class GetDateFilters(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        date_filters = [date_filter.value for date_filter in DateFilters]
        return Response({"results": date_filters}, 200)


class CreateBooking(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def post(self, request, *args, **kwargs):
        request.data['created_by'] = request.user
        new_booking_serializer = NewBookingSerializer(data=request.data)
        if not new_booking_serializer.is_valid():
            return Response(new_booking_serializer.errors, 400)

        # TODO: Not working for multiple products
        products = request.data.pop("products", [])
        if len(products) < 0:
            return Response({"message": "Can't create booking",
                             "errors": "Booking should have more than one product"})

        # TODO: Temporary implementation for single product, should change it to multiple products
        first_product = products[0]
        product_id = first_product.pop('product_id', None)
        quantity = first_product.pop('quantity', None)
        size = first_product.pop('size', None)
        combo_product_details = first_product.pop('combo_product_details', None)
        transport_details = request.data.pop('transport_details', None)
        data = request.data
        data['entity_id'], data['entity_type'] = entity_id_and_entity_type(product_id)

        # Get product values
        product_details = get_product_id_wise_product_details([product_id])

        is_valid, errors = is_product_valid(product_details, product_id, quantity, size, combo_product_details)
        if not is_valid:
            return Response({"message": "Can't create booking", "errors": errors})

        is_valid, errors = check_valid_duration([product_id], data['start_time'], data['end_time'])
        if not is_valid:
            return Response({"message": "Can't create booking", "errors": errors})

        if transport_details:
            if transport_details['km_limit_choosen'] > 0:
                if transport_details['km_limit_choosen'] not in \
                        product_details[product_id]['transport_details']['price_details']:
                    return Response({"message": "Can't create booking", "errors": "Invalid km limit choosen"}, 400)
            is_valid, errors = check_valid_address(transport_details['pickup_location'])
            if not is_valid:
                return Response({"message": "Can't create booking", "errors": errors})
            is_valid, errors = check_valid_address(transport_details['drop_location'])
            if not is_valid:
                return Response({"message": "Can't create booking", "errors": errors})

        all_product_ids, products = combine_all_products(product_id, size, quantity, combo_product_details,\
                                                         product_details)

        is_valid, errors = validate_booking_details(products, data['start_time'], data['end_time'])
        if not is_valid:
            return Response({"message": "Can't create booking", "errors": errors}, 400)

        product_details = get_product_id_wise_product_details(all_product_ids)
        trip_type = transport_details["trip_type"] if transport_details else ""
        km_limit_choosen = transport_details["km_limit_choosen"] if transport_details else 0

        product_price_values = get_product_price_values(
            {
                data['entity_type']: [product_id]
            },
            {
                data['entity_type']: {
                    product_id: {
                        "quantity": quantity,
                        "size": size,
                        "start_time": datetime.strptime(data['start_time'], get_date_format()),
                        "end_time": datetime.strptime(data['end_time'], get_date_format()),
                        "trip_type": trip_type,
                        "discount_percentage": product_details[product_id]["discount"],
                        "km_limit_choosen": km_limit_choosen
                    }
                }
            }
        )

        if len(data['coupon']) == 0:
            coupon_value = get_coupon_value(
                data['coupon'], request.user.id, [data['entity_id']], [product_id],
                data['entity_type'], product_price_values[product_id]['discounted_price'])
        else:
            coupon_value = 0

        total_unique_products = 0
        for each_product in products:
            if each_product['parent_booked_product'] is None:
                total_unique_products += 1

        is_combo = product_details[product_id]['is_combo']
        has_sub_products = product_details[product_id]['has_sub_products']

        for each_product in products:
            if each_product['parent_booked_product'] is not None:
                each_product["coupon_value"] = 0
                each_product["product_value"] = 0
                each_product["is_combo"] = False
                each_product["has_sub_products"] = False
                each_product["transport_details"] = {}
            else:
                each_product["coupon_value"] = coupon_value / total_unique_products
                each_product["product_value"] = product_price_values[product_id]['discounted_price']
                each_product["is_combo"] = is_combo
                each_product["has_sub_products"] = has_sub_products
                each_product["transport_details"] = transport_details

        data['coupon'] = coupon_value
        data['created_by'] = request.user
        data['products'] = products
        # TODO: make modifications to convert the input data into required format for this function,
        #  include coupon logic
        with _booking_lock:
            create_single_booking(data, product_details)

        return Response({"message": "Booking created"}, 200)


class UserBookingsList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    @staticmethod
    def update_response_of_booking(booking):
        booking.pop("coupon", None)
        booking.pop("booking_date", None)
        booking.pop("payment_mode", None)
        booking.pop("total_money", None)
        booking.pop("total_net_value", None)
        booking.pop("total_coupon_discount", None)
        booking.pop("payment_status", None)
        booking.pop("excess_total_price", None)
        booking.pop("excess_total_net_price", None)
        booking.pop("otp", None)
        booking.pop("created_by", None)
        booking.pop("entity_id", None)

    @staticmethod
    def get_booking_id_wise_product_ids(booking_ids):
        booked_products = BookedProducts.objects.filter(booking_id__in=booking_ids).values('booking_id', 'product_id')
        booking_id_wise_product_ids = defaultdict(list)
        product_ids = []
        for product in booked_products:
            product_ids.append(product["product_id"])
            booking_id_wise_product_ids[product["booking_id"]].append(product["product_id"])
        return booking_id_wise_product_ids, product_ids

    @staticmethod
    def get_booking_id_wise_basic_booked_product_details(booking_ids, booking_id_wise_product_ids, product_ids):
        product_id_wise_details = get_product_id_wise_basic_details(product_ids)
        booking_id_wise_product_details = defaultdict(list)
        for booking_id in booking_ids:
            for product_id in booking_id_wise_product_ids[booking_id]:
                booking_id_wise_product_details[booking_id].append(
                    copy.deepcopy(product_id_wise_details[product_id]))
        return booking_id_wise_product_details

    def post(self, request, *args, **kwargs):
        user = request.user
        input_serializer = GetBookingsWithFiltersSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        entity_filters = get_entity_types_filter(request.data['entity_filter'])
        entity_ids = request.data['entity_id']
        status_filters = get_after_booking_confirmation_status_filters(request.data["status_filter"])

        if date_filter == DateFilters.CUSTOM.value:
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != DateFilters.TOTAL.value and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        # TODO: create an active function for user bookings, should return completed bookings too
        self.queryset = Bookings.objects.filter(created_by=user)
        if from_date and to_date:
            self.queryset = self.queryset.filter(
                (Q(start_time__gte=from_date) & Q(start_time__lte=to_date)) |
                (Q(end_time__gte=from_date) & Q(end_time__lte=to_date)) |
                (Q(start_time__lte=from_date) & Q(end_time__gte=to_date))
                )
        if entity_filters:
            self.queryset = self.queryset.filter(entity_type__in=entity_filters)
        if entity_ids:
            self.queryset = self.queryset.filter(entity_id__in=entity_ids)
        if status_filters:
            self.queryset = self.queryset.filter(booking_status__in=status_filters)

        response = super().get(request, *args, **kwargs)
        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])
            self.update_response_of_booking(booking)

        booking_id_wise_product_ids, product_ids = self.get_booking_id_wise_product_ids(booking_ids)
        booking_id_wise_product_details = self.get_booking_id_wise_basic_booked_product_details(
            booking_ids, booking_id_wise_product_ids, product_ids)
        booking_id_wise_amount_earned = booking_id_wise_reward_points_earned(booking_ids)

        # adding ratings to booking products
        booking_id_product_id_wise_ratings = get_booking_id_product_id_wise_ratings(booking_ids, product_ids)
        for booking_id in booking_id_wise_product_details:
            for product in booking_id_wise_product_details[booking_id]:
                key = booking_id + "-" + product["id"]
                product["rating"] = {
                    "rating_given": True if key in booking_id_product_id_wise_ratings else False,
                }
                product["rating"].update(booking_id_product_id_wise_ratings[key])

        for booking in response.data["results"]:
            booking["products"] = booking_id_wise_product_details[booking["id"]]
            booking["rewards_earned"] = booking_id_wise_amount_earned[booking["id"]]
        return response


class CancelBookingView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsOwner |
                          IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookingsSerializer

    def post(self, request, *args, **kwargs):
        # TODO: Should handle refund and update payment details to be payed to entity
        booking = Bookings.objects.filter(id=kwargs['booking_id'])
        if len(booking) == 0:
            return Response({"message": "Can't update booking status", "errors": "Booking does'nt exist"}, 400)

        cancelled_serializer = CancelledDetailsSerializer()
        cancelled_serializer.create(booking[0])
        cancel_booking(kwargs['booking_id'])
        booking.update(booking_status=BookingStatus.CANCELLED.value)
        return Response({"message": "Booking cancelled successfully"}, 200)


class BookingsStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities)

    def post(self, request, *args, **kwargs):
        input_serializer = GetBookingsStatisticsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)
        date_filter = request.data['date_filter']
        entity_filter = get_entity_types_filter(request.data['entity_filter'])
        entity_id = request.data['entity_id']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            previous_from_date = previous_to_date = None
        else:
            from_date, to_date = get_time_period(date_filter)
            previous_from_date, previous_to_date = get_previous_time_period(date_filter)

        if date_filter != DateFilters.TOTAL.value and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        received_bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        cancelled_bookings = CancelledDetails.objects.cancelled_bookings(
            from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        ongoing_bookings = Bookings.objects.ongoing_bookings(entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        pending_bookings = Bookings.objects.pending_bookings(entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        customer_yet_to_take_bookings = Bookings.objects \
            .yet_to_take_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        yet_to_return_bookings = Bookings.objects \
            .yet_to_return_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        customer_taken_bookings = CheckInDetails.objects \
            .customer_taken(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        returned_bookings = CheckOutDetails.objects \
            .returned_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']

        received_percentage_change = cancelled_percentage_change = None
        if date_filter != "Total" and date_filter != "Custom":
            previous_receiving_bookings = Bookings.objects \
                .received_bookings(previous_from_date, previous_to_date, entity_filter, entity_id) \
                .aggregate(count=Count('id'))['count']
            previous_cancelled_bookings = CancelledDetails.objects \
                .cancelled_bookings(previous_from_date, previous_to_date, entity_filter, entity_id) \
                .aggregate(count=Count('id'))['count']

            received_percentage_change = (received_bookings - previous_receiving_bookings) / 100
            cancelled_percentage_change = (cancelled_bookings - previous_cancelled_bookings) / 100

        # TODO: Handle cases for hiding details in Frontend for different date filters
        if date_filter == "Yesterday":
            ongoing_bookings = pending_bookings = -1

        return Response(
            {
                "received": received_bookings,
                "received_percentage_change": received_percentage_change,
                "ongoing": ongoing_bookings,
                "pending": pending_bookings,
                "cancelled": cancelled_bookings,
                "cancelled_percentage_change": cancelled_percentage_change,
                "customer_yet_to_take": customer_yet_to_take_bookings,
                "yet_to_return": yet_to_return_bookings,
                'customer_taken': customer_taken_bookings,
                'returned': returned_bookings
            }, 200)


class GetBookingsStatisticsDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities)
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()

    def post(self, request, *args, **kwargs):
        input_serializer = GetBookingsStatisticsDetailsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        entity_filter = get_entity_types_filter(request.data['entity_filter'])
        entity_id = request.data['entity_id']
        statistics_details_type = request.data['statistics_details_type']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        self.queryset = Bookings.objects.none()
        if statistics_details_type == 'ongoing_bookings':
            self.queryset = Bookings.objects.ongoing_bookings(entity_filter, entity_id)
        elif statistics_details_type == 'pending_bookings':
            self.queryset = Bookings.objects.pending_bookings(entity_filter, entity_id)
        elif statistics_details_type == 'customer_yet_to_take_bookings':
            self.queryset = Bookings.objects.yet_to_take_bookings(from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == 'customer_yet_to_return_bookings':
            self.queryset = Bookings.objects.yet_to_return_bookings(from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == 'customer_taken_bookings':
            booking_ids = CheckInDetails.objects \
                .customer_taken(from_date, to_date, entity_filter, entity_id) \
                .values_list('booking_id', flat=True)
            self.queryset = Bookings.objects.filter(id__in=booking_ids)
        elif statistics_details_type == 'returned_bookings':
            booking_ids = CheckOutDetails.objects \
                .returned_bookings(from_date, to_date, entity_filter, entity_id) \
                .values_list('booking_id', flat=True)
            self.queryset = Bookings.objects.filter(id__in=booking_ids)
        elif statistics_details_type == 'received_bookings':
            self.queryset = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == 'cancelled_bookings':
            booking_ids = CancelledDetails.objects \
                .cancelled_bookings(from_date, to_date, entity_filter, entity_id) \
                .values_list('booking_id', flat=True)
            self.queryset = Bookings.objects.filter(id__in=booking_ids)

        self.queryset = self.queryset.order_by('booking_date')

        response = super().get(request, args, kwargs)
        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])
        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)
        return response


class CancelProductStatusView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwner | IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookedProductsSerializer

    def put(self, request, *args, **kwargs):
        # TODO: Should handle refund and update payment details to be payed to entity
        input_serializer = CancelProductStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        booking_products = BookedProducts.objects \
            .filter(booking=request.data['booking_id'], product_id=request.data['product_id'])
        if len(booking_products) == 0:
            return Response(
                {"message": "Can't cancel product booking",
                 "error": "Invalid Booking id {} or product  {} "
                     .format(request.data['booking_id'], request.data['product_id'])}, 400)

        booking = Bookings.objects.get(id=request.data['booking_id'])
        self.check_object_permissions(request, booking)
        booking_products.update(booking_status=ProductBookingStatus.CANCELLED.value)

        booking_product = booking_products[0]
        create_refund_transaction(
            {
                'booking_id': booking.id, 'entity_id': booking.entity_id,
                'entity_type': booking.entity_type,
                'refund_amount': booking_product.product_value * booking_product.quantity,
                'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                'refund_reason': "Booking Cancelled"
            }
        )
        update_booking_transaction_in_payment(booking.id, False,
                                              booking_product.product_value * booking_product.quantity,
                                              booking_product.net_value * booking_product.quantity,
                                              (booking_product.product_value - booking_product.net_value)
                                              * booking_product.quantity)
        booking.total_money -= booking_product.product_value
        booking.save()

        return Response({"message": "Booking product cancelled successfully"}, 200)


class GetSpecificBookingDetails(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsOwner |
                          IsBookingBusinessClient | IsBookingEmployee)

    def get(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.select_related('created_by').get(id=kwargs['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't get booking details", "error": "Invalid Booking id"}, 400)

        self.check_object_permissions(request, booking)
        user_data = Bookings.objects.none()
        user_data.name = booking.created_by.first_name + " " + booking.created_by.last_name
        user_data.contact_number = booking.created_by.phone_number
        user_data.email = booking.created_by.email
        booking.user_details = user_data

        all_products = BookedProducts.objects.filter(booking=booking)

        combo_products_details = defaultdict(list)
        for each_booked_product in all_products:
            if each_booked_product.hidden:
                combo_products_details[each_booked_product.parent_booked_product.product_id].append(
                    {
                        "product_id": each_booked_product.product_id,
                        "quantity": each_booked_product.quantity,
                        "size": each_booked_product.size,
                    }
                )

        serializer = GetSpecificBookingDetailsSerializer(booking).data
        product_ids = set()
        for booked_product in all_products:
            product_ids.add(booked_product.product_id)
        product_id_wise_product_details = get_product_id_wise_product_details(list(product_ids))
        products = []
        for booked_product in all_products:
            combo_products = []
            if booked_product.hidden is False:
                if booked_product.is_combo or booked_product.has_sub_products:
                    combo_products = combo_products_details[booked_product.product_id]
                products.append(
                    {
                        "product_id": booked_product.product_id,
                        "name": product_id_wise_product_details[booked_product.product_id]["name"],
                        "type": product_id_wise_product_details[booked_product.product_id]["type"],
                        "product_value": booked_product.product_value,
                        "net_value": booked_product.net_value,
                        "coupon_value": booked_product.coupon_value,
                        "booked_quantity": booked_product.quantity,
                        "is_combo": booked_product.is_combo,
                        "has_sub_products": booked_product.has_sub_products,
                        "combo_products": combo_products
                    }
                )
        serializer['total_days'] = get_total_time_period(booking.end_time, booking.start_time)
        serializer['products'] = products
        serializer['outlet_details'] = get_entity_details([booking.entity_id])
        serializer['transaction_details'] = get_transaction_details_by_booking_id(booking.id)
        serializer['transaction_details'] = get_transaction_details_by_booking_id(booking.id)
        serializer['customer_review'] = get_business_client_review_by_booking_id(booking.id)
        return Response(serializer, 200)


class BusinessClientBookingApproval(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBookingBusinessClient
                          | IsBookingEmployee)
    serializer_class = BusinessClientBookingApproval
    queryset = Bookings.objects.all()
    lookup_url_kwarg = "booking_id"

    def put(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.get(id=kwargs['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't get booking details", "error": "Invalid Booking id"}, 400)

        # TODO: Check the approval time is less than the time allocated for approval
        self.check_object_permissions(request, booking)

        current_time = timezone.now() - timedelta(minutes=BookingApprovalTime)
        if current_time > booking.booking_date :
            return Response({"message": "Can't approve the booking",
                             "errors": "This booking is already cancelled"})

        return super().put(request, *args, **kwargs)


class GetBookingCostDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.get(id=kwargs['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't retrieve booking details", "error": "Invalid Booking id"})
        return Response({
            "total_money": booking.total_money,
            "total_coupon_discount": booking.total_coupon_discount
        })


class ProceedToPayment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = ProceedToPaymentSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't make transaction", "errors": input_serializer.errors}, 400)
        payment_mode = request.data['payment_mode']
        booking_id = request.data['booking_id']
        transaction_money = request.data['transaction_money']

        try:
            booking = Bookings.objects.get(id=booking_id)
        except ObjectDoesNotExist:
            return Response({"message": "Can't get booking details", "error": "Invalid Booking id"}, 400)

        booking.payment_mode = payment_mode
        booking.save()

        if payment_mode == PaymentMode.PARTIAL.value:
            if transaction_money != booking.total_money - booking.total_net_value:
                return Response({"message": "Can't create transaction", "errors": "Invalid transaction"}, 400)

            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': booking.entity_id,
                    'entity_type': booking.entity_type,
                    'total_money': booking.total_money - booking.total_net_value,
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.MYC.value, 'paid_by': PaymentUser.CUSTOMER.value
                }
            )

            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': booking.entity_id,
                    'entity_type': booking.entity_type, 'total_money': booking.total_net_value,
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.ENTITY.value, 'paid_by': PaymentUser.CUSTOMER.value
                }
            )
        elif payment_mode == PaymentMode.FULL.value:
            if transaction_money != booking.total_money:
                return Response({"message": "Can't create transaction", "errors": "Invalid transaction"}, 400)
            # this logic should be inside of both cases since we have to check transaction money is valid or not

            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': booking.entity_id,
                    'entity_type': booking.entity_type, 'total_money': booking.total_money,
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.MYC.value, 'paid_by': PaymentUser.CUSTOMER.value
                }
            )

            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': booking.entity_id,
                    'entity_type': booking.entity_type, 'total_money': booking.total_net_value,
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.ENTITY.value, 'paid_by': PaymentUser.MYC.value
                }
            )
        return Response({"message": "Your payment was created successfully"})


class GetBookingDetailsView(generics.ListAPIView):
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities)

    def post(self, request, *args, **kwargs):
        input_serializer = GetBookingDetailsViewSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        entity_filter = get_entity_types_filter(request.data['entity_filter'])
        status_filter = get_status_filters(request.data['status_filter'])
        entity_id = request.data['entity_id']
        from_date, to_date = get_time_period(date_filter)

        # TODO: If you use active here we don't get cancelled bookings
        if from_date and to_date:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date)
                  & Q(entity_type__in=entity_filter) & Q(booking_status__in=status_filter)
                  & Q(entity_id__in=entity_id))).order_by('booking_date')
        elif from_date:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(booking_date__gte=from_date) & Q(entity_type__in=entity_filter)
                  & Q(booking_status__in=status_filter) & Q(entity_id__in=entity_id))).order_by('booking_date')
        elif to_date:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(booking_date__lte=to_date) & Q(entity_type__in=entity_filter)
                  & Q(booking_status__in=status_filter) & Q(entity_id__in=entity_id))).order_by('booking_date')
        else:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(entity_type__in=entity_filter) & Q(booking_status__in=status_filter)
                  & Q(entity_id__in=entity_id))).order_by('booking_date')

        response = super().get(request, args, kwargs)
        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])

        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)
        return response


class BookingStart(APIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee,
                          IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        '''
        'start_details':
        {
            'product_id'(string- 36characters) : {"starting_km": starting_km(int)},
            'product_id'(string- 36characters) : {"starting_km": starting_km(int)}
        }
        '''

        booking = Bookings.objects.get(id=request.data['booking_id'])
        self.check_object_permissions(request, booking)

        input_serializer = BookingStartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        data = request.data.dict()
        data["booking"] = booking
        start_details = data.pop("start_details", None)
        start_details = json.loads(start_details)

        booked_products = BookedProducts.objects.filter(booking=booking, has_sub_products=True)
        transport_details_ids = []
        for each_booking in booked_products:
            transport_details_ids.append(each_booking.id)

        transport_details = TransportBookingDetails.objects.filter(booked_product__in=transport_details_ids)
        for each_transport_data in transport_details:
            try:
                each_transport_data.starting_km_value = \
                    start_details[each_transport_data.booked_product.product_id]['starting_km']
                each_transport_data.save()
            except KeyError:
                return Response({"message": "Can't get booking details",
                                 "error": "Invalid product id"})
        other_images = request.data.pop('other_images', None)

        serializer = CheckInDetailsSerializer()
        check_in = serializer.create(data)

        images = []
        for each_image in other_images:
            all_other_images = {'check_in': check_in, 'image': each_image}
            images.append(all_other_images)
        other_image_serializer = CheckInImagesSerializer()
        other_image_serializer.bulk_create(images)

        update_booking_status(data['booking_id'], BookingStatus.ONGOING.value)
        return Response({"message": "Booking started"}, 200)


class BookingEnd(APIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee,
                          IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        booking = Bookings.objects.get(id=request.data['booking_id'])
        self.check_object_permissions(request, booking)
        input_serializer = BookingEndSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        data = request.data.dict()
        other_images = request.data.pop('product_images', None)
        data.pop('product_images', None)
        review = data.pop('review', None)
        rating = data.pop('rating', None)
        booking_id = request.data['booking_id']

        created_by = request.user
        business_client_review_on_customer(review, rating, booking_id, created_by)

        serializer = CheckOutDetailsSerializer()
        check_out = serializer.create(data)

        images = []
        for each_image in other_images:
            all_product_images = {'check_out': check_out, 'image': each_image}
            images.append(all_product_images)
        product_image_serializer = CheckOutImagesSerializer()
        product_image_serializer.bulk_create(images)

        update_booking_status(data['booking_id'], BookingStatus.COMPLETED.value)
        return Response({"message": "Booking Ended"}, 200)


class GetBookingEndDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee,
                          IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        '''
        'end_details':
        {
            'product_id'(string - 36characters) : {"ending_km" :ending_km(int)},
            'product_id'(string - 36characters) : {"ending_km" :ending_km(int)}
        }
        '''

        booking = Bookings.objects.get(id=kwargs['booking_id'])
        self.check_object_permissions(request, booking)
        try:
            check_in_object = CheckInDetails.objects.get(booking_id=kwargs['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't get booking details", "error": "Invalid booking id"}, 400)

        end_details = request.data.pop("end_details", None)
        booked_products = BookedProducts.objects.select_related('booking').filter(booking_id=kwargs['booking_id'])
        booked_product_serializer = BookedProductsSerializer(booked_products, many=True).data
        transport_details_ids = []
        for each_booking in booked_products:
            transport_details_ids.append(each_booking.id)

        transport_details = TransportBookingDetails.objects.filter(booked_product_id__in=transport_details_ids)
        for each_transport_data in transport_details:
            try:
                each_transport_data.ending_km_value = \
                    end_details[each_transport_data.booked_product.product_id]['ending_km']
                each_transport_data.save()
            except KeyError:
                return Response({"message": "Can't get booking details",
                                 "error": "Invalid product id in booking starting details"})

        products = defaultdict()
        product_ids = []
        for each_booked_product in booked_product_serializer:
            if each_booked_product["parent_booked_product"] is None:
                product_ids.append(each_booked_product["product_id"])
                each_booked_product["start_time"] = booking.start_time.strftime(get_date_format())
                each_booked_product["booking_end_time"] = booking.end_time.strftime(get_date_format())
                each_booked_product["present_end_time"] = (datetime.now()).strftime(get_date_format())
                products[each_booked_product["product_id"]] = each_booked_product

        products_details = get_product_id_wise_product_details(product_ids)

        transport_details = get_transport_details(product_ids)

        for each_product in products:
            #doubt have to reduce discount for excess value
            products[each_product]["discount_percentage"] = products_details[each_product]["discount"]
            products[each_product]["transport_details"] = transport_details[each_product]

        final_product_prices = get_product_prices_by_duration(products)
        excess_price = 0
        excess_net_price = 0
        net_price_values = {}
        for each_product in final_product_prices:
            final_price = final_product_prices[each_product]["final_price"]
            excess_price += final_price
            net_price = get_product_net_price(final_price, "product type")
            net_price_values[each_product] = {"excess_net_price": net_price['net_price'], "excess_price": final_price}
            excess_net_price += net_price['net_price']

        booking.excess_total_price = excess_price
        booking.excess_total_net_price = excess_net_price
        booking.save()

        booked_products_excess_prices = []
        for each_product in booked_products:
            if each_product.parent_booked_product is None:
                update_dict = {"id":each_product.id}
                update_dict.update(net_price_values[each_product.product_id])
                booked_products_excess_prices.append(update_dict)
        booked_product_serializer = BookedProductsSerializer()
        booked_product_serializer.bulk_update(booked_products_excess_prices)

        response_data = get_check_in_details(check_in_object)
        response_data['final_price'] = excess_price + float(booking.total_money)
        response_data['excess_price'] = excess_price
        response_data["extra_information"] = final_product_prices

        create_booking_transaction(
            {
                'booking_id': booking.id, 'entity_id': booking.entity_id,
                'entity_type': booking.entity_type, 'total_money': excess_price,
                'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                'paid_to': PaymentUser.MYC.value, 'paid_by': PaymentUser.CUSTOMER.value
            }
        )

        create_booking_transaction(
            {
                'booking_id': booking.id, 'entity_id': booking.entity_id,
                'entity_type': booking.entity_type, 'total_money': excess_net_price,
                'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                'paid_to': PaymentUser.ENTITY.value, 'paid_by': PaymentUser.MYC.value
            }
        )

        return Response(response_data, 200)


class ReportCustomerForBooking(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee,
                          IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.get(id=request.data['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update details", "error:": "Invalid booking id"}, 400)

        self.check_object_permissions(request, booking)

        request.data['booking'] = booking
        report_customer = ReportCustomerSerializer()
        report_customer.create(request.data)
        return Response({"message": "Reported on customer successfully"}, 200)


class ProductStatistics(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = ProductStatisticsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        product_id = kwargs['product_id']
        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        total_products_available = get_product_details([product_id])[product_id]['quantity']

        total_products_booked = BookedProducts.objects.received_bookings_for_product(
            product_id, from_date, to_date).aggregate(count=Sum(F('quantity')))['count']
        if total_products_booked is None:
            total_products_booked = 0

        total_products_cancelled = BookedProducts.objects.cancelled_bookings_for_product(
            product_id, from_date, to_date).aggregate(count=Sum(F('quantity')))['count']
        if total_products_cancelled is None:
            total_products_cancelled = 0

        remaining_products = total_products_available - total_products_booked + total_products_cancelled

        ongoing_products = BookedProducts.objects.ongoing_bookings_for_product(
            product_id).aggregate(count=Sum(F('quantity')))['count']
        if ongoing_products is None:
            ongoing_products = 0

        return Response(
            {
                "total_products_booked": total_products_booked,
                "total_products_cancelled": total_products_cancelled,
                "remaining_products": remaining_products,
                "ongoing_products": ongoing_products
            }, 200)


class ProductStatisticsDetails(generics.ListAPIView):
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()

    def post(self, request, *args, **kwargs):
        input_serializer = ProductStatisticsDetailsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        product_id = kwargs['product_id']
        date_filter = request.data['date_filter']
        statistics_details_type = request.data['statistics_details_type']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], \
                                 request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        booking_ids = []
        if statistics_details_type == "total_products_booked":
            booking_ids = BookedProducts.objects.received_bookings_for_product(
                product_id, from_date, to_date).values_list('booking_id', flat=True)
        elif statistics_details_type == "total_products_cancelled":
            booking_ids = BookedProducts.objects.cancelled_bookings_for_product(
                product_id, from_date, to_date).values_list('booking_id', flat=True)
        elif statistics_details_type == "ongoing_products":
            booking_ids = BookedProducts.objects.ongoing_bookings_for_product(product_id) \
                .values_list('booking_id', flat=True)

        self.queryset = Bookings.objects.filter(id__in=booking_ids)
        response = super().get(request, args, kwargs)

        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])
        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)

        return response


class ReportCustomerReasonsList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReportCustomerReasons.objects.all()
    serializer_class = ReportCustomerResonsSerializer


class ReportCustomerReasonsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReportCustomerReasons.objects.all()
    serializer_class = ReportCustomerResonsSerializer


class GetBookingDetailsOfProductId(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee |
                          IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()

    def get(self, request, *args, **kwargs):
        booking_ids = BookedProducts.objects.select_related('booking') \
            .filter(product_id=kwargs['product_id']).values_list('booking_id', flat=True)
        self.queryset = Bookings.objects.filter(id__in=booking_ids)
        response = super().get(request, args, kwargs)

        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])

        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)
        return response


class BusinessClientProductCancellationDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = BusinessClientProductCancellationSerializer(data=request.data)
        if input_serializer.is_valid():
            booked_product = BookedProducts.objects.filter(booking=request.data['booking_id'],
                                                           product_id=request.data['product_id'])
            if len(booked_product) == 0:
                return Response(
                    {"message": "Can't cancel the product", "errors": "There is no product{}in booking id {}"
                        .format(request.data['product_id'], request.data['booking_id'])}, 400)
            request.data['cancelled_by'] = request.user.id
            input_serializer.save()

            # TODO: create refund transactions here
            booked_product.update(booking_status=ProductBookingStatus.CANCELLED.value)
            return Response({"message": "Successfully cancelled the product"}, 200)

        else:
            return Response({"message": "Can't cancel the product", "errors": input_serializer.errors}, 400)


def create_multiple_bookings_while_checkout(all_booking):
    overall_is_valid = True
    all_errors = defaultdict(list)
    product_details = all_booking.pop('all_product_details', None)

    after_grouping_of_bookings = {}

    for each_booking in all_booking:
        product_list = all_booking[each_booking]['products']
        booking_products = []
        for each_product in product_list:
            if not each_product['is_combo'] and not each_product['has_sub_products']:
                booking_products.append(each_product)
        final_products_list = combine_products(booking_products)
        after_grouping_of_bookings[each_booking] = final_products_list

        is_valid, errors = validate_booking_product_details(
            product_details, final_products_list, all_booking[each_booking]['start_time'],
            all_booking[each_booking]['end_time'])
        if not is_valid:
            overall_is_valid = True
            all_errors[each_booking].append(errors)
    if not overall_is_valid:
        return overall_is_valid, all_errors

    with _booking_lock:
        for each_booking in all_booking:
            is_valid, errors = validate_booking_product_availability(
                product_details, after_grouping_of_bookings[each_booking],
                all_booking[each_booking]['start_time'], all_booking[each_booking]['end_time'])

            if not is_valid:
                overall_is_valid = False
                all_errors[each_booking].append(errors)
        if overall_is_valid:
            for each_booking in all_booking:
                create_single_booking(all_booking[each_booking],product_details)
        return overall_is_valid, all_errors


def create_single_booking(booking_object, product_values):

    product_list = booking_object.pop('products', None)
    total_money = 0.0
    total_coupon_discount = 0.0
    for product in product_list:
        if product['parent_booked_product'] is None:
            total_money += float(product['product_value'])
            total_coupon_discount += float(product['coupon_value'])

    booking_object['total_money'] = total_money
    booking_object['total_coupon_discount'] = total_coupon_discount

    total_net_value = 0

    combo_parent_products = []
    sub_products_parent_products = []
    product_list_copy = product_list[::]
    for product in product_list_copy:
        net_value = get_product_net_price(float(product['product_value']), "product_type")
        product["product_value"] = product_values[product['product_id']]['price'] * product['quantity']
        product['price'] = product_values[product['product_id']]['price_by_type']
        product['price_type'] = product_values[product['product_id']]['price_type']

        net_value = product_values[product['product_id']]['net_value_details']['net_price'] * product['quantity']
        product['net_value'] = net_value
        if product['is_combo']:
            combo_product = product
            product_list.remove(product)
            combo_product['hidden'] = False
            total_net_value += net_value
            combo_parent_products.append(combo_product)

        elif product['has_sub_products']:
            sub_product = product
            product_list.remove(product)
            sub_product['hidden'] = False
            total_net_value += net_value
            sub_products_parent_products.append(sub_product)

        elif product['parent_booked_product'] is None:
            product['hidden'] = False
            total_net_value += net_value
        else:
            product['hidden'] = True
            product["product_value"] = 0
            product['net_value'] = 0

    booking_object["total_net_value"] = total_net_value

    bookings_serializer = BookingsSerializer()
    booking = bookings_serializer.create(booking_object)

    booked_product_serializer_object = BookedProductsSerializer()

    if "event_type" in booking_object and booking_object["event_type"] == EntityType.EVENT.value:
        for each_product in product_list:
            each_event_data = each_product["event_details"]
            event_product = booked_product_serializer_object.create({
                'booking': booking,
                'product_id': each_product['product_id'],
                'quantity': each_product['quantity'],
                'is_combo': True,
                "has_sub_products": False,
                'product_value': each_event_data["total_price"],
                'net_value': each_event_data["total_price"],
                'coupon_value': each_product['coupon_value']
            })

            price_details = each_event_data.pop("prices", None)
            each_event_data["cart_product"] = event_product

            events_details_serializer = EventsDetailsSerializer()
            event_details_object = events_details_serializer.create(each_event_data)

            for each_price in price_details:
                each_price["event_details"] = event_details_object

            events_prices_serializer = EventsPricesSerializer()
            events_prices_serializer.bulk_create(price_details)
    else:
        booked_combo_products = defaultdict()
        for each_combo_product in combo_parent_products:
            combo_product = booked_product_serializer_object.create({
                'booking': booking,
                'product_id': each_combo_product['product_id'],
                'quantity': each_combo_product['quantity'],
                'is_combo': True,
                "has_sub_products": False,
                'product_value': each_combo_product['product_value'],
                'net_value': each_combo_product['net_value'],
                'coupon_value': each_combo_product['coupon_value']
            })
            booked_combo_products[each_combo_product['product_id']] = combo_product

        for each_sub_product in sub_products_parent_products:
            sub_product = booked_product_serializer_object.create({
                'booking': booking,
                'product_id': each_sub_product['product_id'],
                'quantity': each_sub_product['quantity'],
                'is_combo': False,
                "has_sub_products": True,
                'product_value': each_sub_product['product_value'],
                'net_value': each_sub_product['net_value'],
                'coupon_value': each_sub_product['coupon_value']
            })
            booked_combo_products[each_sub_product['product_id']] = sub_product

            transport_data = product_values[sub_product.product_id]['transport_details']
            transport_details = each_sub_product['transport_details']
            km_limit_choosen = transport_details['km_limit_choosen']
            transport_details_serializer = TransportBookingDetailsSerializer()
            transport_distance_details_serializer = TransportBookingDistanceDetailsSerializer()
            transport_duration_details_serializer = TransportBookingDurationDetailsSerializer()
            if km_limit_choosen > 0:
                transport_distance_details_object = transport_distance_details_serializer\
                    .create(transport_data['price_details'][km_limit_choosen])

                transport_duration_details_object = None
            else:
                try:
                    transport_distance_details_object = transport_distance_details_serializer\
                        .create(transport_data['price_details'])
                    transport_duration_details_object = transport_duration_details_serializer\
                        .create(transport_data['duration_details'])
                except:
                    transport_distance_details_object = None
                    transport_duration_details_object = None
            make_your_own_trip_object = None
            if "make_your_own_trip" in transport_details:
                make_your_own_trip_data = transport_details["make_your_own_trip"]
                make_your_own_trip_serializer = MakeYourOwnTripDetailsSerializer()
                make_your_own_trip_object = make_your_own_trip_serializer.create(make_your_own_trip_data)

            transport_details_serializer.create({
                'booked_product': sub_product,
                'trip_type': transport_details['trip_type'],
                'pickup_location': transport_details['pickup_location'],
                'drop_location': transport_details['drop_location'],
                'km_limit_choosen': km_limit_choosen,
                'distance_details': transport_distance_details_object,
                'duration_details': transport_duration_details_object,
                "make_your_own_trip_details": make_your_own_trip_object
            })

        for each_booked_product in product_list:
            each_booked_product['booking'] = booking
            if each_booked_product['parent_booked_product'] is not None:
                each_booked_product['parent_booked_product'] = booked_combo_products[
                    each_booked_product['parent_booked_product']]
        booked_product_serializer_object.bulk_create(product_list)

    # TODO: To be added when celery is working
    # TODO: To automatically cancel booking if business client didn't accept request after some interval
    # current_time = datetime.utcnow()
    # current_time.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
    # cancel_booking_if_not_accepted_by_business_client.apply_async(
    #     (booking.id, ), eta=current_time + timedelta(seconds=60))

    return True, {}


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


class UserSelectQuotation(generics.UpdateAPIView):
    serializer_class = UserSelectQuotationSerializer
    queryset = Bookings.objects.all()


def get_transport_details(product_ids):
    booked_products_transport_details = TransportBookingDetails.objects.select_related('booked_product')\
        .filter(booked_product__product_id__in=product_ids)

    booked_products_transport_data = {}
    for each_transport_data in booked_products_transport_details:
        booked_products_transport_data[each_transport_data.booked_product.product_id] = each_transport_data

    transport_details = defaultdict()
    for each_product in product_ids:
        if each_product in booked_products_transport_data:
            each_product_transport_data = booked_products_transport_data[each_product]

            transport_details[each_product] = {
                "trip_type": each_product_transport_data.trip_type,
                "starting_km_value": each_product_transport_data.starting_km_value,
                "ending_km_value": each_product_transport_data.ending_km_value,
                "km_limit_choosen": each_product_transport_data.km_limit_choosen,
                "distance_details": {
                    "km_hour_limit": each_product_transport_data.distance_details.km_hour_limit,
                    "km_day_limit": each_product_transport_data.distance_details.km_day_limit,
                    "excess_km_price": each_product_transport_data.distance_details.excess_km_price,
                    "is_infinity": each_product_transport_data.distance_details.is_infinity,
                    "single_trip_return_value_per_km":
                        each_product_transport_data.distance_details.single_trip_return_value_per_km,
                    "price": each_product_transport_data.distance_details.price,
                    "km_limit": each_product_transport_data.distance_details.km_limit
                }
            }
            if each_product_transport_data.duration_details is not None:
                transport_details[each_product].update(
                    {"duration_details": {
                        "hour_price": each_product_transport_data.duration_details.hour_price,
                        "day_price": each_product_transport_data.duration_details.day_price,
                        "excess_hour_duration_price":
                            each_product_transport_data.duration_details.excess_hour_duration_price,
                        "excess_day_duration_price":
                            each_product_transport_data.duration_details.excess_day_duration_price
                    }}
                )
            else:
                transport_details[each_product].update({"duration_details":{}})
        else:
            transport_details[each_product] = {}

    return transport_details


class MakeYourOwnTripBooking(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        input_serializer = MakeYourOwnTripBookingSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"Message":"Can't make booking", "errors": input_serializer.errors}, 400)
        trip_details = request.data['trip_details']
        is_valid, errors = check_valid_address(trip_details['pickup_location'])
        if not is_valid:
            return Response({"Message":"Can't make booking", "errors": errors}, 400)
        is_valid, errors = check_valid_address(trip_details['drop_location'])
        if not is_valid:
            return Response({"Message":"Can't make booking", "errors": errors}, 400)

        is_valid, errors = validate_start_end_time(request.data['start_time'], request.data['end_time'])
        if not is_valid:
            return Response({"Message": "Can't make booking", "errors": errors}, 400)

        product_id = request.data['product_id']
        preferred_vehicle_id = trip_details['preferred_vehicle']

        product_details = get_product_id_wise_product_details([product_id, preferred_vehicle_id])

        if len(product_details) != 2:
            return Response({"Message": "Can't make booking", "errors": "Invalid Product Id or Preferred Vehicle ID"}, 400)

        entity_id, entity_type = entity_id_and_entity_type(product_id)
        pickup_location_id = post_create_address(trip_details['pickup_location'])["address_id"]
        drop_location_id = post_create_address(trip_details['drop_location'])["address_id"]

        product_data = [
            {
                "product_id": product_id, "quantity": 1, "size": None, "parent_booked_product": None, "coupon_value": 0,
                "product_value": 0, "is_combo": False, "has_sub_products": True,
                "transport_details": {
                    "trip_type": trip_details["trip_type"],
                    "pickup_location": pickup_location_id,
                    "drop_location": drop_location_id,
                    "km_limit_choosen": 0,
                    "make_your_own_trip":{
                        "preferred_vehicle": trip_details['preferred_vehicle'],
                        "no_of_adults": trip_details['no_of_adults'], "no_of_children" : trip_details["no_of_children"],
                        "no_of_vehicles": trip_details["no_of_vehicles"], "min_budget": trip_details["min_budget"],
                        "max_budget": trip_details["max_budget"]
                    }
                }
            }
        ]

        booking_details = {
            "coupon": "", "created_by": request.user, "entity_id": entity_id, "entity_type": entity_type,
            "start_time": request.data['start_time'], "end_time": request.data['end_time'],
            "products": product_data
        }

        is_valid, errors = create_single_booking(booking_details, product_details)

        if not is_valid:
            return Response({"message":"Can't create booking", "errors": errors}, 400)

        return Response({"product details": product_details}, 200)
