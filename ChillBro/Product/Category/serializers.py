from rest_framework import serializers
from .models import Category, CategoryImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryImage
        fields = '__all__'


class AllTopLevelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    icon_url = serializers.CharField(required=True)


class CategoryTopeLevelListSerializer(serializers.Serializer):
    all_levels = AllTopLevelSerializer(many=True)

