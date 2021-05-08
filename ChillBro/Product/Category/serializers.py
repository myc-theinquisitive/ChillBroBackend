from rest_framework import serializers
from .models import Category, CategoryImage, CategoryPrices


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryImage
        fields = '__all__'


class CategoryPricesSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryPrices
        fields = '__all__'



