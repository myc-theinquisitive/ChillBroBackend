from .serializers import *


def insertRating(validated_data):
    rating_serializer = ReviewsRatingsSerializer()
    return rating_serializer.create(validated_data)


def ReviewByBookingId(booking_id):
    try:
        review = ReviewsRatings.objects.get(related_id=booking_id)
        return CustomerReviewSerializer(review).data
    except:
        return {}
