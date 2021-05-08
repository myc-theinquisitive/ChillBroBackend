from django.db.models import Count

from .BaseProduct.models import Product, ProductImage
from .BaseProduct.views import productNetPrice
from .Seller.models import SellerProduct


def product_data_prices(product_ids):
    products = Product.objects.filter(id__in=product_ids)
    product_prices = {}
    for each_product in products:
        discount = ((each_product.price - each_product.discounted_price) / each_product.price) * 100
        product_prices[each_product.id] = {'price':each_product.price,\
                                           'net_value': productNetPrice(each_product.price, discount),\
                                           'quantity': each_product.quantity}
    return product_prices


def product_details(product_ids):
    products = Product.objects.filter(id__in=product_ids)
    details_of_product = {}
    for each_product in products:
        details_of_product[each_product.id] = {'name':each_product.name,
                                               'type':each_product.type}
    return details_of_product


def get_entity_id_and_entity_type(product_id):
    try:
        seller = SellerProduct.objects.select_related('product').get(product=product_id)
    except:
        return None, None
    return seller.seller_id, seller.product.type


def product_details_with_image(product_ids):
    products = ProductImage.objects.select_related('product').filter(product_id__in=product_ids, order = 0)
    details_of_product = {}
    for each_product in products:
        details_of_product[each_product.product.id] = {'name':each_product.product.name,
                                               'image_url':each_product.image.url}
    return details_of_product


def total_products_count_in_entities(entity_ids):
    products_count = SellerProduct.objects.filter(seller_id__in=entity_ids).aggregate(count = Count('product'))['count']
    return products_count
