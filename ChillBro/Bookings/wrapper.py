

def get_product_data(product_id_list):
    products = {}
    products['1'] = {'value': 100.0}
    products['2'] = {'value': 200.0}
    products['3'] = {'value': 300.0}
    return products


def get_total_products_value(products_id_list):
    products = get_product_data(products_id_list)
    total_money = 0.0
    for i in products_id_list:
        total_money += products[i["product_id"]]['value']*int(i['quantity'])
    return total_money

def get_individual_product_value(product_id):
    product = get_product_data([product_id])
    return product[product_id]['value']
def get_coupons():
    coupons = ['a', 'b', 'c']
    return coupons