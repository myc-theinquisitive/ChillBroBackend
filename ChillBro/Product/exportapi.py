from collections import defaultdict
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Min
from .Category.models import Category
from .BaseProduct.models import Product, ProductImage
from .views import calculate_product_net_price
from .Seller.models import SellerProduct
from django.db.models import Count
from .BaseProduct.constants import ActivationStatus


def get_product_id_wise_details(product_ids):
    products = Product.objects.filter(id__in=product_ids)
    if not products:
        products = []

    product_id_wise_details = defaultdict(dict)
    for each_product in products:
        discount = ((each_product.price - each_product.discounted_price) / each_product.price) * 100
        product_data = {
            'product_id': each_product.id,
            'price': each_product.discounted_price,
            'net_value_details': calculate_product_net_price(each_product.price, discount),
            'quantity': each_product.quantity,
            'name': each_product.name,
            'type': each_product.type
        }
        product_id_wise_details[each_product.id] = product_data
    return product_id_wise_details


def get_entity_id_and_entity_type(product_id):
    try:
        seller = SellerProduct.objects.select_related('product').get(product=product_id)
    except ObjectDoesNotExist:
        return None, None
    return seller.seller_id, seller.product.type


def product_details(product_ids):
    from .views import ProductView
    product_view = ProductView()
    return product_view.get_by_ids(product_ids)


def total_products_count_in_entities(entity_ids):
    products_count = SellerProduct.objects.filter(seller_id__in=entity_ids,
                                                  product__activation_status=ActivationStatus.ACTIVE.value)\
                        .aggregate(count=Count('product'))['count']
    return products_count


def check_product_is_valid(product_id):
    try:
        Product.objects.get(id=product_id)
        return True
    except ObjectDoesNotExist:
        return False
        
        
def top_level_categories():
    return Category.objects.filter(parent_category=None).values_list('name', flat=True)
    

def seller_products_starting_price_query(seller_id):
    return SellerProduct.objects.filter(seller_id=seller_id).select_related('Product').values('seller_id') \
        .annotate(starting_price=Min('product__discounted_price')).values('starting_price')


def get_sellers_product_stating_price(seller_ids):
    return SellerProduct.objects.filter(seller_id__in=seller_ids).select_related('Product').values('seller_id') \
        .annotate(starting_price=Min('product__discounted_price')).values('seller_id', 'starting_price')
