from rest_framework import serializers
from .models import ReviewsRatings, BCAppFeedbackAndSuggestions, CustomerAppFeedbackAndSuggestions, \
    CustomerAppRating, BCAppRating


class ReviewsRatingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewsRatings
        fields = '__all__'


class CustomerReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(required=True)
    comment = serializers.CharField(required=True)


class CustomDatesSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(required=True)
    to_date = serializers.DateTimeField(required=True)


class EntityTotalReviewsSerializer(serializers.Serializer):
    date_filter = serializers.CharField(required=True)
    entity_filters = serializers.ListField(
        child=serializers.CharField()
    )
    comment_required = serializers.BooleanField(required=True)
    rating_filters = serializers.ListField(
        child=serializers.CharField()
    )
    custom_dates = CustomDatesSerializer(required=False)
    entity_ids = serializers.ListField(
        child=serializers.CharField()
    )


class BCAppFeedbackAndSuggestionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BCAppFeedbackAndSuggestions
        fields = '__all__'


class GetBCAppFeedbackAndSuggestionsSerializer(serializers.Serializer):
    category_filters = serializers.ListField(
        child=serializers.CharField()
    )


class CustomerAppFeedbackAndSuggestionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerAppFeedbackAndSuggestions
        fields = '__all__'


class GetCustomerAppFeedbackAndSuggestionsSerializer(serializers.Serializer):
    category_filters = serializers.ListField(
        child=serializers.CharField()
    )
    module_filters = serializers.ListField(
        child=serializers.CharField()
    )


class EntityReviewStatisticsSerializer(serializers.Serializer):
    entity_ids = serializers.ListField(
        child=serializers.CharField()
    )
    entity_filters = serializers.ListField(
        child=serializers.CharField()
    )


class CustomerAppRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerAppRating
        fields = '__all__'


class BCAppRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = BCAppRating
        fields = '__all__'
