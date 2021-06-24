from .constants import ItemType


def get_wishlist_product_ids(user_id, product_ids):
    from .models import WishList
    return WishList.objects.filter(
        created_by_id=user_id, related_id__in=product_ids, item_type=ItemType.PRODUCT.value)\
        .values_list('related_id', flat=True)


def get_wishlist_entity_ids(user_id, entity_ids):
    from .models import WishList
    return WishList.objects.filter(
        created_by_id=user_id, related_id__in=entity_ids, item_type=ItemType.ENTITY.value)\
        .values_list('related_id', flat=True)
