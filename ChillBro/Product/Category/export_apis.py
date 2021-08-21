from collections import defaultdict

from .models import Category
from .serializers import CategorySerializer


def category_details(category_ids):
    categories = Category.objects.filter(id__in=category_ids)
    category_serializer = CategorySerializer(categories, many=True).data
    category_details = defaultdict()
    for each_category in category_serializer:
        category_details[each_category["id"]] = each_category
    return category_details