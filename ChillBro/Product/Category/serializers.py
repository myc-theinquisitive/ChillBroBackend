from rest_framework import serializers
from django.conf import settings
from .models import Category, CategoryImage, CategoryPrices


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
    
    def to_representation(self, data):
        data = super(CategorySerializer, self).to_representation(data)
        data['icon_url'] = data.get('icon_url').replace(settings.IMAGE_REPLACED_STRING, '')
        return data

    def create(self, validated_data):
        return super().create(validated_data)


class CategoryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryImage
        fields = '__all__'

        
class CategoryPricesSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryPrices
        fields = '__all__'
