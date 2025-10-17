from django.test import TestCase
from inventory.models import InventoryItem
from inventory.commands import CommandInvoker, AgregarProductoCommand, AgregarStockCommand
from inventory.repositories import DjangoInventoryRepo
from core.models import GrainType

class CommandIntegrationTest(TestCase):
    def setUp(self):
        self.repo = DjangoInventoryRepo()
        # Crear un request mock mejorado para CommandInvoker
        class MockSession(dict):
            modified = False
            
            def setdefault(self, key, default):
                if key not in self:
                    self[key] = default
                return self[key]
            
            def save(self):
                pass

        class MockRequest:
            def __init__(self):
                self.session = MockSession()

        self.request = MockRequest()

    def test_command_invoker_integration(self):
        """Prueba de integración del CommandInvoker con comandos reales"""
        invoker = CommandInvoker(self.request)
        
        # 1. Comando: Agregar producto
        item_data = {
            'sku': 'INTEG-001',
            'name': 'Café Integración',
            'type': GrainType.ROBUSTA,
            'stock_kg': 30.0,
            'min_stock_kg': 8.0
        }
        
        add_product_cmd = AgregarProductoCommand(self.repo, item_data)
        result1 = invoker.execute_command(add_product_cmd)
        
        # Verificar que se creó
        item = InventoryItem.objects.get(sku='INTEG-001')
        self.assertEqual(item.stock_kg, 30.0)
        self.assertIn('agregado exitosamente', result1)
        
        # 2. Comando: Agregar stock
        add_stock_cmd = AgregarStockCommand(self.repo, 'INTEG-001', 20.0)
        result2 = invoker.execute_command(add_stock_cmd)
        
        # Verificar que se actualizó
        item.refresh_from_db()
        self.assertEqual(item.stock_kg, 50.0)
        self.assertIn('Agregados 20.0kg', result2)
        
        # 3. Probar el historial de comandos
        history = invoker.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['type'], 'AgregarProductoCommand')
        self.assertEqual(history[1]['type'], 'AgregarStockCommand')
        
        # 4. Probar undo del último comando (AgregarStockCommand)
        undo_result = invoker.undo_last()
        item.refresh_from_db()
        self.assertEqual(item.stock_kg, 30.0)  # Debería volver al stock original
        self.assertIn('revertido', undo_result)
        
        # 5. Probar undo del primer comando (AgregarProductoCommand)
        undo_result2 = invoker.undo_last()
        with self.assertRaises(InventoryItem.DoesNotExist):
            InventoryItem.objects.get(sku='INTEG-001')  # El producto debería eliminarse
        self.assertIn('eliminado', undo_result2)