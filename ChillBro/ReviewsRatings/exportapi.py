from django.db.models import Avg
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


def average_rating_query_for_secondary_related_id(secondary_related_id):
    return ReviewsRatings.objects.filter(secondary_related_id=secondary_related_id).values('rating')\
                .annotate(avg_rating=Avg('rating')).values('avg_rating')


def get_secondary_related_id_wise_average_rating(secondary_related_ids):
    return ReviewsRatings.objects.filter(secondary_related_id__in=secondary_related_ids) \
        .annotate(avg_rating=Avg('rating')).values('avg_rating', 'secondary_related_id')
