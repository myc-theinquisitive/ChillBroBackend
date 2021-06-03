from collections import defaultdict
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from .Category.models import Category
from .BaseProduct.models import Product, ProductImage, ComboProductItems, ProductSize
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
            'product_id':each_product.id,
            'price': each_product.discounted_price,
            'net_value_details': calculate_product_net_price(each_product.price, discount),
            'quantity': each_product.quantity,
            'name': each_product.name,
            'type': each_product.type,
            'has_sizes':each_product.has_sizes,
            'is_combo':each_product.is_combo
        }
        product_sizes_details = {}
        if each_product.has_sizes:
            all_sizes_products = ProductSize.objects.filter(product_id=each_product.id)

            for each_size_product in all_sizes_products:
                product_sizes_details[each_size_product.size] = each_size_product.quantity

        product_data['size_products'] = product_sizes_details
        combo_products = defaultdict()
        if each_product.is_combo:
            all_combo_products = ComboProductItems.objects.select_related('product') \
                .filter(product_id = each_product.id)

            for each_combo_product in all_combo_products:
                combo_product_data = {
                    "quantity":each_combo_product.quantity
                }
                combo_products[each_combo_product.combo_item.id] = combo_product_data
        product_data['combo_products'] = combo_products
        product_id_wise_details[each_product.id] = product_data

    return product_id_wise_details


def get_entity_id_and_entity_type(product_id):
    try:
        seller = SellerProduct.objects.select_related('product').get(product=product_id)
    except ObjectDoesNotExist:
        return None, None
    return seller.seller_id, seller.product.type


def product_details_with_image(product_ids):
    # Doubt: have to change the image order to either 1 or 0
    products = ProductImage.objects.select_related('product').filter(product_id__in=product_ids, order=1)
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
        
        
def top_level_categories():
    return Category.objects.filter(parent_category=None).values_list('name',flat=True)
    
    
