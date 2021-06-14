from rest_framework import serializers
from .models import *


class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'
        read_only_fields = ('booking_status', 'total_money', 'payment_status')


class BookedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedProducts
        fields = '__all__'

    def bulk_create(self, validated_data):
        new_products = []
        for product in validated_data:
            add_booking_product = BookedProducts(
                booking=product["booking"],
                product_id=product["product_id"],
                product_value=product["product_value"],
                quantity=product["quantity"],
                net_value=product["net_value"],
                size = product["size"],
                is_combo = product["is_combo"],
                has_sub_products = product["has_sub_products"],
                hidden = product["hidden"],
                parent_booked_product = product["parent_booked_product"],
                coupon_value = product["coupon_value"]
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

    def create(self, booking):
        return CancelledDetails.objects.create(booking=booking)


class CheckInImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInImages
        fields = '__all__'

    def bulk_create(self, images):
        all_images = []
        for image in images:
            each_image = CheckInImages(
                check_in=image['check_in'],
                image=image['image']
            )
            all_images.append(each_image)
        return CheckInImages.objects.bulk_create(all_images)


class CheckOutImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOutImages
        fields = '__all__'

    def bulk_create(self, images):
        all_images = []
        for image in images:
            each_image = CheckOutImages(
                check_out=image['check_out'],
                image=image['image']
            )
            all_images.append(each_image)
        return CheckOutImages.objects.bulk_create(all_images)


class ReportCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientReportOnCustomer
        fields = '__all__'

    def create(self, validated_data):
        object = BusinessClientReportOnCustomer(
            booking=validated_data['booking'],
            reasons_selected=validated_data['reasons_selected'],
            additional_info=validated_data['additional_info']
        )
        return object.save()


class BusinessClientProductCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientProductCancellation
        fields = '__all__'


class ReportCustomerResonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCustomerReasons
        fields = '__all__'


class UpdateBookingIdSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)
    booking_status = serializers.CharField(required=True)


class BookedProductSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    quantity = serializers.IntegerField(required=True)


class NewBookingSerializer(serializers.Serializer):
    products = BookedProductSerializer(many=True)
    entity_type = serializers.CharField(required=True, max_length=30)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    payment_mode = serializers.CharField(required=True, max_length=30)


class CustomDatesSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(required=True)
    to_date = serializers.DateTimeField(required=True)


class BookingStatisticsSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_filter = serializers.ListField(
        child=serializers.CharField()
    )
    entity_id = serializers.ListField(
        child=serializers.CharField(min_length=36, max_length=36)
    )
    custom_dates = CustomDatesSerializer(required=False)


class GetBookingsStatisticsDetailsSerializer(BookingStatisticsSerializer):
    statistics_details_type = serializers.CharField(required=True)


class CancelProductStatusSerializer(serializers.Serializer):
    booking_id = serializers.CharField(required=True, min_length=36, max_length=36)
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    contact_number = serializers.CharField(required=True)
    email = serializers.CharField(required=True)


class GetSpecificBookingDetailsSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, min_length=36, max_length=36)
    booking_date = serializers.DateTimeField(required=True)
    total_money = serializers.DecimalField(decimal_places=2, max_digits=20)
    booking_status = serializers.CharField(required=True)
    entity_id = serializers.CharField(required=True, min_length=36, max_length=36)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    payment_status = serializers.CharField(max_length=30)
    payment_mode = serializers.CharField(max_length=30)
    user_details = UserSerializer()


class GetBookingDetailsViewSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_filter = serializers.ListField(
        child=serializers.CharField()
    )
    status_filter = serializers.ListField(
        child=serializers.CharField()
    )
    entity_id = serializers.ListField(
        child=serializers.CharField()
    )


class BookingStartSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)
    id_proof_type = serializers.CharField(required=True)
    id_image = serializers.FileField(required=True)
    other_images = serializers.ListField(
        child=serializers.FileField()
    )


class BookingEndSerializer(serializers.Serializer):
    booking_id = serializers.CharField(min_length=36, max_length=36)
    caution_deposit_deductions = serializers.CharField()
    rating = serializers.CharField()
    product_images = serializers.ListField(
        child=serializers.FileField()
    )


class ProductStatisticsSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    custom_dates = CustomDatesSerializer(required=False)


class ProductStatisticsDetailsSerializer(ProductStatisticsSerializer):
    statistics_details_type = serializers.CharField(required=True)


class ProductAvailabilitySerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=36)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class BusinessClientBookingApproval(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ('id','booking_status')


class MakeTransactionSerializer(serializers.Serializer):
    transaction_type = serializers.CharField(required=True)
    booking_id = serializers.CharField(required=True, min_length=36, max_length=36)
    transaction_money = serializers.DecimalField(decimal_places=2, max_digits=20)