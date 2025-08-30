from dataclasses import dataclass
from typing import List, Protocol
from datetime import date, timedelta

# ------------ Singleton (GestorDeInventario) ------------
class InventoryManager:
    _instance = None

    def __new__(cls, repo):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.repo = repo
        return cls._instance

    def add_stock(self, sku: str, kg: float):
        item = self.repo.get_item(sku)
        item.stock_kg += kg
        self.repo.save(item)
        return item

    def consume_stock(self, sku: str, kg: float):
        item = self.repo.get_item(sku)
        item.stock_kg -= kg
        self.repo.save(item)
        return item

# Repositorio mínimo apoyado en Django ORM
class DjangoInventoryRepo:
    from core.models import InventoryItem, PurchaseOrder

    def get_item(self, sku):
        return self.InventoryItem.objects.get(sku=sku)

    def save(self, item):
        item.save()

    def ensure_min_stock(self, item):
        if item.stock_kg < item.min_stock_kg:
            # genera OC básica
            self.PurchaseOrder.objects.create(
                supplier="Proveedor Base",
                item=item,
                qty_kg=item.min_stock_kg * 2,
                status='pending'
            )
            return True
        return False

# ------------ Factory Method (Productos por tipo de café) ------------
class CoffeeProduct(Protocol):
    def label(self) -> str: ...

@dataclass
class ArabicaCoffee:
    weight_kg: float
    def label(self) -> str: return f"Arábica {self.weight_kg}kg"

@dataclass
class RobustaCoffee:
    weight_kg: float
    def label(self) -> str: return f"Robusta {self.weight_kg}kg"

@dataclass
class BlendCoffee:
    weight_kg: float
    ratio: str = "60/40"
    def label(self) -> str: return f"Blend {self.ratio} {self.weight_kg}kg"

class ProductFactory:
    @staticmethod
    def create(kind: str, weight_kg: float) -> CoffeeProduct:
        if kind == 'arabica':  return ArabicaCoffee(weight_kg)
        if kind == 'robusta':  return RobustaCoffee(weight_kg)
        if kind == 'blend':    return BlendCoffee(weight_kg)
        raise ValueError("Tipo de café no soportado")

# ------------ Abstract Factory (Combos) ------------
@dataclass
class Mug:      design: str
@dataclass
class Filter:   size: str

@dataclass
class Combo:
    coffee: CoffeeProduct
    mug: Mug
    filter: Filter

class ComboFactory(Protocol):
    def create_combo(self, kind: str, weight_kg: float) -> Combo: ...

class DefaultComboFactory:
    def create_combo(self, kind: str, weight_kg: float) -> Combo:
        coffee = ProductFactory.create(kind, weight_kg)
        mug = Mug(design="Taza Café Aroma")
        filtr = Filter(size="V60-02")
        return Combo(coffee, mug, filtr)

# ------------ Adapter (Proveedor/logística externa) ------------
class ExternalLogisticsAPI:
    def ship(self, order_id: int, priority: bool) -> str:
        return f"EXT-{order_id}-{'FAST' if priority else 'ECON'}"

class ProviderAdapter:
    """Adapta la API externa a nuestra interfaz interna simple."""
    def __init__(self, provider: ExternalLogisticsAPI):
        self.provider = provider

    def create_shipment(self, order_id: int, speed: str) -> str:
        return self.provider.ship(order_id, priority=(speed == 'fast'))

# ------------ Composite (Proceso de producción) ------------
class ProcessComponent(Protocol):
    def execute(self) -> str: ...

@dataclass
class BasicProcess(ProcessComponent):
    name: str
    def execute(self) -> str: return f"{self.name} OK"

class ProcessComposite(ProcessComponent):
    def __init__(self, name: str):
        self.name = name
        self.children: List[ProcessComponent] = []
    def add(self, comp: ProcessComponent): self.children.append(comp)
    def execute(self) -> str:
        results = [c.execute() for c in self.children]
        return f"{self.name}: " + " -> ".join(results)

# ------------ Facade (Producción) ------------
class ProductionFacade:
    def __init__(self, inv_manager: InventoryManager):
        self.inv = inv_manager

    def plan_and_run(self, sku: str, kg: float, kind: str):
        # consumir materia prima
        item = self.inv.consume_stock(sku, kg)
        # pipeline compuesto: tostado -> molido -> empaque
        pipeline = ProcessComposite("Lote Café")
        pipeline.add(BasicProcess("Tostado"))
        pipeline.add(BasicProcess("Molido"))
        pipeline.add(BasicProcess("Empaque"))
        executed = pipeline.execute()
        # crear lote terminado (simplificado)
        from core.models import ProductBatch
        batch = ProductBatch.objects.create(
            code=f"LOT-{sku}-{date.today().strftime('%Y%m%d')}",
            coffee_type=kind,
            qty_kg=kg,
            expiry_date=date.today() + timedelta(days=365)
        )
        return executed, batch, item
