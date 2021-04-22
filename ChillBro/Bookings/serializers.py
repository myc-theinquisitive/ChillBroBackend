from rest_framework import serializers
from .models import *


class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'


class BookedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedProducts
        fields = '__all__'

    def bulk_create(self, validated_data):
        new_products = []
        for product in validated_data:
            add_booking_product = BookedProducts(
                booking_id=product["booking_id"],
                product_id=product["product_id"],
                product_value=product["product_value"],
                quantity=product["quantity"]
            )
            new_products.append(add_booking_product)
        return BookedProducts.objects.bulk_create(new_products)


class CheckInDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInDetails
        fields = '__all__'


class CheckOutDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOutDetails
        fields = '__all__'


class CancelledDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelledDetails
        fields = '__all__'


class OtherImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherImages
        fields = '__all__'

    def bulk_create(self, images):
        all_images = []
        for image in images:
            each_image = OtherImages(
                check_in=image['check_in'],
                other_image_id=image['other_image_id']
            )
            all_images.append(each_image)
        return OtherImages.objects.bulk_create(all_images)


class CheckOutProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOutProductImages
        fields = '__all__'

    def bulk_create(self, images):
        print(images)
        all_images = []
        for image in images:
            each_image = CheckOutProductImages(
                check_out=image['check_out'],
                product_image_id=image['product_image_id']
            )
            all_images.append(each_image)
        return CheckOutProductImages.objects.bulk_create(all_images)


class TransactionDetailsSerializer(serializers.Serializer):
    class Meta:
        model = TransactionDetails
        fields = '__all__'


class BusinessClientReportOnCustomerSerializer(serializers.Serializer):
    class Meta:
        model = BusinessClientReportOnCustomer
        fields = '__all__'

    def create(self, validated_data):
        object = BusinessClientReportOnCustomer(
            booking_id=validated_data['booking_id'],
            reasons_selected=validated_data['reasons_selected'],
            additional_info=validated_data['additional_info']
        )
        return object.save()


class BookingIdSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)
    product_status = serializers.ListField(
        child=serializers.CharField()
    )


class CancelOrderSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)


class UpdateBookingIdSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)
    booking_status = serializers.CharField(required=True)


class NewProductSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    quantity = serializers.IntegerField(required=True)


class NewBookingSerializer(serializers.Serializer):
    coupon = serializers.CharField(required=True, min_length=36, max_length=36)
    products = NewProductSerializer(many=True)
    entity_type = serializers.CharField(required=True)
    payment_status = serializers.CharField(required=True)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)


class StatisticsSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)


class GetBookingsStatisticsDetailsSerializer(StatisticsSerializer):
    statistics_details_type = serializers.CharField(required=True)


class OrderDetailsSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_filter = serializers.ListField(
        child=serializers.CharField()
    )
    status = serializers.ListField(
        child=serializers.CharField()
    )
    payment_status = serializers.ListField(
        child=serializers.CharField()
    )


class UpdateProductStatusSerializer(serializers.Serializer):
    booking_id = serializers.CharField(required=True, min_length=36, max_length=36)
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)
    product_status = serializers.CharField(required=True)


class PaymentRevenueStatisticsViewSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    contact_number = serializers.CharField(required=True)
    email = serializers.CharField(required=True)


class TransactionSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=True)
    utr = serializers.CharField(required=True)
    mode = serializers.CharField(required=True)
    transaction_date = serializers.DateTimeField(required=True)


class CustomerReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(required=True)
    review = serializers.CharField(required=True)


class GetSpecificBookingDetailsSerializer(serializers.Serializer):
    booking_id = serializers.CharField(required=True, min_length=36, max_length=36)
    booking_date = serializers.DateTimeField(required=True)
    total_money = serializers.DecimalField(decimal_places=2, max_digits=20)
    booking_status = serializers.CharField(required=True)
    payment_status = serializers.CharField(required=True)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    products = NewProductSerializer(many=True)
    User_Details = UserSerializer()
    transaction_details = TransactionSerializer(required=False)
    customer_review = CustomerReviewSerializer(required=False)


class GetBookingDetailsViewSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    category_filter = serializers.ListField(
        child=serializers.CharField()
    )
    status_filter = serializers.ListField(
        child=serializers.CharField()
    )
    entity_id = serializers.ListField(
        child=serializers.CharField()
    )


class BookingStartSerializer(serializers.Serializer):
    booking_id_id = serializers.CharField(min_length=36, max_length=36)
    id_proof_type = serializers.CharField(required=True)
    id_image = serializers.FileField(required=True)
    other_images = serializers.ListField(
        child=serializers.FileField()
    )


class BookingEndSerializer(serializers.Serializer):
    booking_id_id = serializers.CharField(min_length=36, max_length=36)
    caution_deposit_deductions = serializers.CharField()
    rating = serializers.CharField()
    product_images = serializers.ListField(
        child=serializers.FileField()
    )
