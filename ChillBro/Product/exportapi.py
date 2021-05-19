from collections import defaultdict
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
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


def product_details_with_image(product_ids):
    products = ProductImage.objects.select_related('product').filter(product_id__in=product_ids, order=0)
    details_of_product = {}
    for each_product in products:
        image_url = each_product.image.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING,"")
        details_of_product[each_product.product.id] = {
            'name': each_product.product.name,
            'image_url': image_url
        }
    return details_of_product


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
