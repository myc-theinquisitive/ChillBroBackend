from .views import is_product_valid


def check_is_product_valid(product_details, product_id, quantity, all_sizes, combo_product_details):
    return is_product_valid(product_details, product_id, quantity, all_sizes, combo_product_details)


def form_all_products(product_id, size, quantity, combo_product_details, product_details):
    from .views import combine_all_products
    return combine_all_products(product_id, size, quantity, combo_product_details, product_details)