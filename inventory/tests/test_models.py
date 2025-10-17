from django.test import TestCase
from inventory.models import InventoryItem, RawGrain
from core.models import GrainType

class InventoryItemModelTest(TestCase):
    def setUp(self):
        self.item = InventoryItem.objects.create(
            sku='TEST-001',
            name='Café Test',
            type=GrainType.ARABICA,
            stock_kg=50.0,
            min_stock_kg=10.0
        )

    def test_inventory_item_creation(self):
        """Prueba la creación correcta de un item de inventario"""
        self.assertEqual(self.item.sku, 'TEST-001')
        self.assertEqual(self.item.name, 'Café Test')
        self.assertEqual(self.item.type, GrainType.ARABICA)
        self.assertEqual(self.item.stock_kg, 50.0)
        self.assertEqual(self.item.min_stock_kg, 10.0)

    def test_update_stock(self):
        """Prueba el método update_stock"""
        self.item.update_stock(25.0)
        self.assertEqual(self.item.stock_kg, 75.0)
        
        self.item.update_stock(-20.0)
        self.assertEqual(self.item.stock_kg, 55.0)

    def test_needs_restock(self):
        """Prueba el método needs_restock"""
        # Stock suficiente
        self.item.stock_kg = 50.0
        self.assertFalse(self.item.needs_restock())
        
        # Stock en el límite - AHORA ESPERA TRUE
        self.item.stock_kg = 10.0
        self.assertTrue(self.item.needs_restock())  # Cambiado de assertFalse a assertTrue
        
        # Stock bajo
        self.item.stock_kg = 5.0
        self.assertTrue(self.item.needs_restock())