from django.core.exceptions import ObjectDoesNotExist
from .models import InventoryItem

class DjangoInventoryRepo:
    def get_item(self, sku: str) -> InventoryItem:
        try:
            return InventoryItem.objects.get(sku=sku)
        except InventoryItem.DoesNotExist:
            raise ObjectDoesNotExist(f"InventoryItem with SKU {sku} does not exist")
    
    def save(self, item: InventoryItem):
        item.save()
    
    def ensure_min_stock(self, item: InventoryItem) -> bool:
        return not item.needs_restock()