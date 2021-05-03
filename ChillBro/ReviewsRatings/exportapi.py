from .serializers import *


def insert_rating(validated_data):
    rating_serializer = ReviewsRatingsSerializer()
    return rating_serializer.create(validated_data)


def review_by_booking_id(booking_id):
    try:
        review = ReviewsRatings.objects.get(related_id=booking_id)
        return CustomerReviewSerializer(review).data
    except:
        return {}
