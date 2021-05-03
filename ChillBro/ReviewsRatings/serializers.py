from rest_framework import serializers

from .models import ReviewsRatings


class ReviewsRatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewsRatings
        fields = '__all__'

    def create(self, validated_data):
        object = ReviewsRatings(
            related_id=validated_data['related_id'],
            comment=validated_data['comment'],
            rating=validated_data['rating'],
            created_by=validated_data['created_by']
        )
        return object.save()


class CustomerReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(required=True)
    comment = serializers.CharField(required=True)


class CustomDatesSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(required=True)
    to_date = serializers.DateTimeField(required=True)


class EntityTotalReviewsSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    category_filters = serializers.ListField(
        child = serializers.CharField()
    )
    comment_required = serializers.BooleanField(required=True)
    rating_filters = serializers.ListField(
        child = serializers.CharField()
    )
    custom_dates = CustomDatesSerializer(required=False)
