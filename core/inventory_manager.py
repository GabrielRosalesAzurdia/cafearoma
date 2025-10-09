from django.core.exceptions import ObjectDoesNotExist
from inventory.models import InventoryItem, PurchaseOrder
from .observers import Subject

class InventoryManager(Subject):
    _instance = None
    _observers = []
    
    def __new__(cls, repo=None):
        if cls._instance is None:
            cls._instance = super(InventoryManager, cls).__new__(cls)
            cls._instance.repo = repo
            cls._instance._observers = []
        return cls._instance

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    def add_stock(self, sku: str, kg: float) -> InventoryItem:
        try:
            item = self.repo.get_item(sku)
            item.update_stock(kg)
            self.repo.save(item)
            # Notificar después de agregar stock
            self.notify()
            return item
        except ObjectDoesNotExist:
            raise ValueError(f"Item con SKU {sku} no encontrado")
    
    def consume_stock(self, sku: str, kg: float) -> InventoryItem:
        try:
            item = self.repo.get_item(sku)
            if item.stock_kg >= kg:
                item.update_stock(-kg)
                self.repo.save(item)
                # Notificar después de consumir stock
                self.notify()
                return item
            else:
                raise ValueError(f"Stock insuficiente para {sku}")
        except ObjectDoesNotExist:
            raise ValueError(f"Item con SKU {sku} no encontrado")
    
    def check_low_stock(self):
        low_stock_items = []
        items = InventoryItem.objects.all()
        for item in items:
            if item.needs_restock():
                low_stock_items.append(item)
        return low_stock_items