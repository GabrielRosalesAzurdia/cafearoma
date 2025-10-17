from django.test import TestCase
from inventory.models import InventoryItem
from inventory.commands import AgregarProductoCommand, AgregarStockCommand
from inventory.repositories import DjangoInventoryRepo
from core.models import GrainType

class CommandPatternTest(TestCase):
    def setUp(self):
        self.repo = DjangoInventoryRepo()
        # No necesitamos el invoker para estas pruebas

    def test_agregar_producto_command(self):
        """Prueba el comando AgregarProductoCommand directamente"""
        item_data = {
            'sku': 'NEW-001',
            'name': 'Nuevo Café',
            'type': GrainType.ARABICA,
            'stock_kg': 25.0,
            'min_stock_kg': 5.0
        }
        
        command = AgregarProductoCommand(self.repo, item_data)
        result = command.execute()
        
        # Verificar que se creó el producto
        item = InventoryItem.objects.get(sku='NEW-001')
        self.assertEqual(item.name, 'Nuevo Café')
        self.assertEqual(item.stock_kg, 25.0)
        
        # Probar undo
        undo_result = command.undo()
        with self.assertRaises(InventoryItem.DoesNotExist):
            InventoryItem.objects.get(sku='NEW-001')

    def test_agregar_stock_command(self):
        """Prueba el comando AgregarStockCommand directamente"""
        # Primero crear un producto
        item = InventoryItem.objects.create(
            sku='TEST-002',
            name='Café Test',
            type=GrainType.ARABICA,
            stock_kg=10.0,
            min_stock_kg=5.0
        )
        
        command = AgregarStockCommand(self.repo, 'TEST-002', 15.0)
        result = command.execute()
        
        # Verificar que se actualizó el stock
        item.refresh_from_db()
        self.assertEqual(item.stock_kg, 25.0)
        
        # Probar undo
        command.undo()
        item.refresh_from_db()
        self.assertEqual(item.stock_kg, 10.0)