from core.services.patterns import InventoryManager, DjangoInventoryRepo, ProductionFacade

def run_demo_production(sku: str, kg: float, kind: str):
    inv = InventoryManager(DjangoInventoryRepo())
    facade = ProductionFacade(inv)
    return facade.plan_and_run(sku, kg, kind)
