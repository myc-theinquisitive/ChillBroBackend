def getProductData(product_id_list):
    # here have to wirte orm query to fetch the product details having products_id in product_id_list
    products = {'df8966f9-f6ce-4a46-9a00-80ac3988f818': {'price': 100.0},
                'df8966f9-f6ce-4a46-9a00-80ac3988f819': {'price': 200.0},
                'df8966f9-f6ce-4a46-9a00-80ac3988f820': {'price': 300.0}}
    if len(products) == 0:
        return None
    return products




def getIndividualProductValue(product_ids):
    product = getProductData(product_ids)
    return product


def getCouponValue(coupon_id, product_ids, entity_ids, total_money):
    return True, 100.0
    # return False, 0


def getCoupons(coupon_id):
    coupons = ['df8966f9-f6ce-4a46-9a00-80ac3988f821', 'df8966f9-f6ce-4a46-9a00-80ac3988f822',
               'df8966f9-f6ce-4a46-9a00-80ac3988f823']
    if coupon_id in coupons:
        return coupon_id
    return None
