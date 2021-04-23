from .serializers import *


def insertRating(validated_data):
    print('exportapi')
    print(validated_data)
    rating_serializer = ReviewsRatingsSerializer()
    return rating_serializer.create(validated_data)
