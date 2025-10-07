from django.db import models
from django.utils import timezone
from core.models import ProcessStage, GrainType

class ProductionTask(models.Model):
    stage = models.CharField(max_length=2, choices=ProcessStage.choices, default=ProcessStage.TOSTADO)
    assigned_unit = models.CharField(max_length=100)
    planned_kg = models.FloatField()
    progress = models.IntegerField(default=0)  # Cambiado a IntegerField para porcentaje entero
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_stage_index = models.IntegerField(default=0)
    
    # Etapas en orden
    STAGES_ORDER = [
        ProcessStage.TOSTADO,
        ProcessStage.MOLIDO, 
        ProcessStage.ENVASADO,
        ProcessStage.COMPLETADO
    ]
    
    def get_current_stage(self):
        """Obtiene la etapa actual basada en el índice"""
        if self.current_stage_index < len(self.STAGES_ORDER):
            return self.STAGES_ORDER[self.current_stage_index]
        return ProcessStage.COMPLETADO
    
    def advance_stage(self):
        """Avanza a la siguiente etapa de producción"""
        if self.current_stage_index < len(self.STAGES_ORDER) - 1:
            self.current_stage_index += 1
            self.stage = self.STAGES_ORDER[self.current_stage_index]
            
            # Calcular progreso como entero (0-100%)
            total_stages = len(self.STAGES_ORDER) - 1  # -1 porque empezamos en 0
            self.progress = int((self.current_stage_index / total_stages) * 100)
            self.save()
            
            # Si llegó a la última etapa, marcar como completado
            if self.current_stage_index == len(self.STAGES_ORDER) - 1:
                self.mark_done()
            
            return True
        return False
    
    def mark_done(self):
        """Marca la tarea como completada"""
        self.progress = 100
        self.stage = ProcessStage.COMPLETADO
        self.completed_at = timezone.now()
        self.save()
    
    def get_remaining_stages(self):
        """Obtiene las etapas restantes"""
        return self.STAGES_ORDER[self.current_stage_index + 1:]
    
    def __str__(self):
        return f"{self.get_stage_display()} - {self.assigned_unit}"

class ProductBatch(models.Model):
    code = models.CharField(max_length=50, unique=True)
    coffee_type = models.CharField(max_length=2, choices=GrainType.choices)
    qty_kg = models.FloatField()
    cupping_score = models.FloatField(null=True, blank=True)
    mfg_date = models.DateField()
    expiry_date = models.DateField()
    production_task = models.ForeignKey(ProductionTask, on_delete=models.CASCADE, related_name='batches')
    
    def __str__(self):
        return f"Batch {self.code} - {self.get_coffee_type_display()}"