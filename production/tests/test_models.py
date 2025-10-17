from django.test import TestCase
from production.models import ProductionTask, ProductBatch
from core.models import ProcessStage, GrainType

class ProductionTaskModelTest(TestCase):
    def setUp(self):
        self.task = ProductionTask.objects.create(
            stage=ProcessStage.TOSTADO,
            assigned_unit="Línea Test",
            planned_kg=10.0,
            progress=0
        )

    def test_production_task_creation(self):
        """Prueba la creación de tarea de producción"""
        self.assertEqual(self.task.stage, ProcessStage.TOSTADO)
        self.assertEqual(self.task.assigned_unit, "Línea Test")
        self.assertEqual(self.task.planned_kg, 10.0)
        self.assertEqual(self.task.progress, 0)

    def test_advance_stage(self):
        """Prueba el avance de etapas de producción"""
        # Avanzar de TOSTADO a MOLIDO
        self.task.advance_stage()
        self.assertEqual(self.task.stage, ProcessStage.MOLIDO)
        self.assertEqual(self.task.progress, 33)
        
        # Avanzar de MOLIDO a ENVASADO
        self.task.advance_stage()
        self.assertEqual(self.task.stage, ProcessStage.ENVASADO)
        self.assertEqual(self.task.progress, 66)
        
        # Avanzar de ENVASADO a COMPLETADO
        self.task.advance_stage()
        self.assertEqual(self.task.stage, ProcessStage.COMPLETADO)
        self.assertEqual(self.task.progress, 100)

    def test_mark_done(self):
        """Prueba marcar tarea como completada"""
        self.task.mark_done()
        self.assertEqual(self.task.stage, ProcessStage.COMPLETADO)
        self.assertEqual(self.task.progress, 100)
        self.assertIsNotNone(self.task.completed_at)

class ProductBatchModelTest(TestCase):
    def test_product_batch_creation(self):
        """Prueba la creación de lote de producto"""
        task = ProductionTask.objects.create(
            stage=ProcessStage.COMPLETADO,
            assigned_unit="Línea Test",
            planned_kg=5.0,
            progress=100
        )
        
        batch = ProductBatch.objects.create(
            code='BATCH-TEST-001',
            coffee_type=GrainType.ARABICA,
            qty_kg=5.0,
            cupping_score=85.5,
            mfg_date='2024-01-01',
            expiry_date='2025-01-01',
            production_task=task
        )
        
        self.assertEqual(batch.code, 'BATCH-TEST-001')
        self.assertEqual(batch.coffee_type, GrainType.ARABICA)
        self.assertEqual(batch.qty_kg, 5.0)
        self.assertEqual(batch.cupping_score, 85.5)
        self.assertEqual(batch.production_task, task)