from django.test import TestCase
from inventory.models import InventoryItem
from production.models import ProductionTask, ProductBatch
from core.models import GrainType
from core.inventory_manager import InventoryManager
from inventory.repositories import DjangoInventoryRepo

class ProductionFlowIntegrationTest(TestCase):
    def setUp(self):
        # Crear item de inventario
        self.inventory_item = InventoryItem.objects.create(
            sku='ARAB-TEST',
            name='Arábica Test',
            type=GrainType.ARABICA,
            stock_kg=100.0,
            min_stock_kg=10.0
        )
        
        # Inicializar manager de inventario
        self.repo = DjangoInventoryRepo()
        self.inventory_manager = InventoryManager(self.repo)

    def test_complete_production_flow(self):
        """Prueba de integración: flujo completo de producción"""
        # 1. Verificar stock inicial
        initial_stock = self.inventory_item.stock_kg
        self.assertEqual(initial_stock, 100.0)
        
        # 2. Crear tarea de producción
        task = ProductionTask.objects.create(
            stage='TO',  # Tostado
            assigned_unit="Línea de Integración",
            planned_kg=25.0,
            progress=0
        )
        
        # 3. Simular consumo de materia prima
        updated_item = self.inventory_manager.consume_stock('ARAB-TEST', 25.0)
        self.assertEqual(updated_item.stock_kg, 75.0)
        
        # 4. Avanzar etapas de producción
        task.advance_stage()  # Tostado → Molido
        self.assertEqual(task.stage, 'MO')
        self.assertEqual(task.progress, 33)
        
        task.advance_stage()  # Molido → Envasado
        self.assertEqual(task.stage, 'EN')
        self.assertEqual(task.progress, 66)
        
        task.advance_stage()  # Envasado → Completado
        self.assertEqual(task.stage, 'CO')
        self.assertEqual(task.progress, 100)
        
        # 5. Crear lote de producto terminado
        batch = ProductBatch.objects.create(
            code='BATCH-INTEG-001',
            coffee_type=GrainType.ARABICA,
            qty_kg=25.0,
            cupping_score=88.0,
            mfg_date='2024-01-01',
            expiry_date='2025-01-01',
            production_task=task
        )
        
        # 6. Verificar que todo está conectado correctamente
        self.assertEqual(batch.production_task, task)
        self.assertEqual(batch.qty_kg, 25.0)
        self.assertEqual(task.planned_kg, 25.0)