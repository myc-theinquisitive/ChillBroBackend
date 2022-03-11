from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Min
from .Category.models import Category
from .BaseProduct.models import Product, ComboProductItems, ProductSize
from .HireAVehicle.models import HireAVehicle
from .SelfRental.models import SelfRental
from .views import calculate_product_net_price
from django.db.models import Count
from .product_view import ProductView
from Entity.export_apis import get_entity_type_and_sub_type


# TODO: This is not optimized calls are going exponential
def get_product_id_wise_details(product_ids):
    products = Product.objects.filter(id__in=product_ids)
    sub_products_ids = ProductView().get_sub_products_ids(product_ids)
    transport_details = get_transport_details(product_ids)
    event_details = get_event_details(product_ids)

    if not products:
        products = []

    product_id_wise_details = defaultdict(dict)
    for each_product in products:
        try:
            discount = ((each_product.price - each_product.discounted_price) / each_product.price) * 100
        except:
            discount = 0
        has_sub_products = each_product.has_sub_products
        if each_product.type == "MAKE_YOUR_OWN_TRIP":
            has_sub_products = True

        product_data = {
            'product_id': each_product.id,
            'price': each_product.discounted_price,
            'price_by_type': each_product.price,
            'price_type': each_product.price_type,
            'net_value_details': calculate_product_net_price(each_product.price, discount),
            'discount': discount,
            'quantity_unlimited': each_product.quantity_unlimited,
            'quantity': each_product.quantity,
            'name': each_product.name,
            'type': each_product.type,
            'has_sizes':each_product.has_sizes,
            'is_combo':each_product.is_combo,
            'has_sub_products': has_sub_products
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
            combo_item_ids = []
            for each_combo_item in all_combo_products:
                combo_item_ids.append(each_combo_item.combo_item.id)
            from Product.BaseProduct.views import get_product_sizes
            product_sizes = get_product_sizes(combo_item_ids)

            for each_combo_product in all_combo_products:
                combo_item_sizes = product_sizes[each_combo_product.combo_item.id]
                combo_product_data = {
                    "quantity":each_combo_product.quantity,
                    "sizes": combo_item_sizes
                }
                combo_products[each_combo_product.combo_item.id] = combo_product_data
        product_data['combo_products'] = combo_products
        sub_products = defaultdict()
        if each_product.has_sub_products:
            sub_products = sub_products_ids[each_product.id]

        product_data['sub_products'] = sub_products
        if each_product.id in transport_details:
            product_data['transport_details'] = transport_details[each_product.id]
        else:
            product_data['transport_details'] = {}

        if each_product.id in event_details:
            product_data['event_details'] = event_details[each_product.id]
        else:
            product_data['event_details'] = {}

        product_id_wise_details[each_product.id] = product_data

    return product_id_wise_details


def get_entity_id_and_entity_type(product_id):
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return None, None
    entity_type, entity_sub_type = get_entity_type_and_sub_type(product.seller_id)
    return product.seller_id, entity_type


def product_details(product_ids):
    from .views import ProductView
    product_view = ProductView()
    return product_view.get_by_ids(product_ids)


def total_products_count_in_entities(entity_ids):
    products_count = Product.objects.filter(seller_id__in=entity_ids).active()\
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
    return Product.objects.filter(seller_id=seller_id).values('seller_id') \
        .annotate(starting_price=Min('discounted_price')).values('starting_price')


def get_sellers_product_stating_price(seller_ids):
    return Product.objects.filter(seller_id__in=seller_ids).values('seller_id') \
        .annotate(starting_price=Min('discounted_price')).values('seller_id', 'starting_price')


def check_valid_duration_for_products(product_ids, start_time, end_time):
    from .views import ProductView
    product_view = ProductView()
    return product_view.check_valid_duration(product_ids, start_time, end_time)


def get_product_values(group_product_ids_by_type, group_product_details_by_type):
    from .views import ProductView
    product_view = ProductView()
    return product_view.calculate_starting_prices(group_product_ids_by_type, group_product_details_by_type)


def get_product_final_prices(products):
    from .views import ProductView
    product_view = ProductView()
    return product_view.calculate_final_prices(products)


def get_transport_details(product_ids):
    transport_details = defaultdict()
    from Product.HireAVehicle.views import HireAVehicleView
    hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
    hire_a_vehicles_price_details = HireAVehicleView().get_price_data(hire_a_vehicles)
    hire_a_vehicle_duration_details = HireAVehicleView().get_duration_data(hire_a_vehicles)
    for each_product in hire_a_vehicles:
        transport_details[each_product.product_id] = {
            "price_details": hire_a_vehicles_price_details[each_product.product_id],
            "duration_details": hire_a_vehicle_duration_details[each_product.product_id]
        }
    from Product.SelfRental.views import SelfRentalView
    self_rentals = SelfRental.objects.filter(product_id__in=product_ids)
    self_rentals_price_details = convert_dict_of_list_to_dict_of_dict(SelfRentalView().get_price_data(self_rentals))
    self_rentals_duration_details = SelfRentalView().get_duration_data(self_rentals)

    for each_product in self_rentals:
        transport_details[each_product.product_id] = {
            "price_details": self_rentals_price_details[each_product.product_id],
            "duration_details": self_rentals_duration_details[each_product.product_id]
        }

    return transport_details


def get_event_details(product_ids):
    from Product.Events.views import EventView
    event_details_with_product_ids = defaultdict()
    event_details = EventView().get_by_ids(product_ids)

    for each_event in event_details:
        event_details_with_product_ids[each_event["product"]] = each_event

    return event_details_with_product_ids


def calculate_product_excess_net_price(excess_price, product_type):
    from .views import calculate_net_price
    return calculate_net_price(excess_price, product_type)
    
    
def convert_dict_of_list_to_dict_of_dict(dict_elements):
    resultant_dict = defaultdict(dict)
    for each_product in dict_elements:
        for each_km_limit in dict_elements[each_product]:
            resultant_dict[each_product][each_km_limit['km_limit']] = each_km_limit
    return resultant_dict


def get_basic_details(product_ids):
    from .BaseProduct.views import get_product_basic_details
    return get_product_basic_details(product_ids)
