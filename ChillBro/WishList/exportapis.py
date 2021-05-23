def get_wishlist_product_ids(user_id, product_ids):
    from .models import WishList
    return WishList.objects.filter(created_by_id=user_id, product_id__in=product_ids)\
        .values_list('product_id', flat=True)
