from .composite import ProcessComposite, BasicProcess
from .models import ProductionTask, ProductBatch
from core.inventory_manager import InventoryManager
from core.factories import ProductFactory
from inventory.repositories import DjangoInventoryRepo
from core.models import ProcessStage, GrainType
from django.utils import timezone
import random

class ProductionFacade:
    def __init__(self, inv_manager: InventoryManager):
        self.inv_manager = inv_manager
        self.product_factory = ProductFactory()

    def create_production_process(self) -> ProcessComposite:
        """Crea el proceso compuesto de producción de café con etapas separadas"""
        main_process = ProcessComposite("Producción de Café Gourmet")
        
        # Definir las etapas del proceso
        stages = [
            ("Calibración de tostadora y preparación", 1),
            ("Tostado controlado por temperatura", 2),
            ("Enfriamiento rápido del grano", 1),
            ("Ajuste de molino para molido", 1),
            ("Molido fino/medio/grueso", 1),
            ("Control de consistencia del molido", 1),
            ("Limpieza de línea de envasado", 1),
            ("Sellado al vacío", 1),
            ("Etiquetado y codificación", 1),
            ("Control de calidad final", 1)
        ]
        
        for stage_name, duration in stages:
            main_process.add(BasicProcess(stage_name, duration))
        
        return main_process

    def start_production(self, sku: str, kg: float, kind: str, coffee_type: str = "AR") -> dict:
        """Inicia una nueva producción (solo consume materia prima y crea la tarea)"""
        try:
            # 1. Verificar y consumir materia prima
            inventory_item = self.inv_manager.consume_stock(sku, kg)
            
            # 2. Crear proceso de producción
            production_process = self.create_production_process()
            
            # 3. Crear tarea de producción (inicia en etapa 0)
            production_task = ProductionTask.objects.create(
                stage=ProcessStage.TOSTADO,
                assigned_unit="Línea de Producción 1",
                planned_kg=kg,
                progress=0,
                current_stage_index=0
            )
            
            return {
                'success': True,
                'production_task': production_task,
                'inventory_item': inventory_item,
                'production_process': production_process,
                'message': f'✅ Producción iniciada. Tarea #{production_task.id} creada.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def advance_production_stage(self, task_id: int) -> dict:
        """Avanza a la siguiente etapa de producción"""
        try:
            task = ProductionTask.objects.get(id=task_id)
            
            # Avanzar etapa en la tarea
            if task.advance_stage():
                # Crear lote de producto si se completó todo
                if task.stage == ProcessStage.COMPLETADO:
                    return self._create_product_batch(task)
                else:
                    return {
                        'success': True,
                        'task': task,
                        'message': f'✅ Avanzado a {task.get_stage_display()}. Progreso: {task.progress}%'
                    }
            else:
                return {
                    'success': False,
                    'error': 'No se puede avanzar - producción ya completada'
                }
                
        except ProductionTask.DoesNotExist:
            return {
                'success': False,
                'error': 'Tarea de producción no encontrada'
            }

    def _create_product_batch(self, task: ProductionTask) -> dict:
        """Crea el lote de producto terminado cuando se completa la producción"""
        try:
            # Crear producto usando Factory
            coffee_product = self.product_factory.create('arabica', task.planned_kg)  # Tipo hardcodeado por simplicidad
            
            # Crear lote de producto terminado
            batch_code = f"BATCH-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            product_batch = ProductBatch.objects.create(
                code=batch_code,
                coffee_type='AR',  # Hardcodeado por simplicidad
                qty_kg=task.planned_kg,
                cupping_score=round(random.uniform(80.0, 95.0), 1),
                mfg_date=timezone.now().date(),
                expiry_date=timezone.now().date() + timezone.timedelta(days=365),
                production_task=task
            )
            
            return {
                'success': True,
                'task': task,
                'product_batch': product_batch,
                'message': f'🎉 Producción COMPLETADA! Lote {batch_code} creado.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear lote: {str(e)}'
            }

    def get_production_status(self, task_id: int) -> dict:
        """Obtiene el estado detallado de una tarea de producción"""
        try:
            task = ProductionTask.objects.get(id=task_id)
            return {
                'task': task,
                'current_stage': task.get_stage_display(),
                'progress': task.progress,
                'is_complete': task.stage == ProcessStage.COMPLETADO,
                'remaining_stages': task.get_remaining_stages()
            }
        except ProductionTask.DoesNotExist:
            return {'error': 'Tarea no encontrada'}

    def generate_production_report(self) -> str:
        """Genera reporte de producción"""
        tasks = ProductionTask.objects.all()
        completed_tasks = tasks.filter(stage=ProcessStage.COMPLETADO)
        in_progress_tasks = tasks.exclude(stage=ProcessStage.COMPLETADO)
        
        report = [
            "📊 REPORTE DE PRODUCCIÓN - CAFÉ AROMA",
            "=" * 50,
            f"Total de tareas: {len(tasks)}",
            f"Completadas: {len(completed_tasks)}",
            f"En progreso: {len(in_progress_tasks)}",
            "",
            "Tareas en progreso:"
        ]
        
        for task in in_progress_tasks.order_by('-created_at')[:5]:
            report.append(f"  - Tarea #{task.id}: {task.get_stage_display()} - {task.progress}%")
        
        return "\n".join(report)