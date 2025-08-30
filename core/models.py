from django.db import models
from django.utils import timezone

# --- Gestión de Materia Prima ---
class GrainType(models.TextChoices):
    ARABICA = 'arabica', 'Arábica'
    ROBUSTA = 'robusta', 'Robusta'
    BLEND   = 'blend', 'Blend'

class RawGrain(models.Model):
    supplier = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=GrainType.choices)
    origin = models.CharField(max_length=120, blank=True)
    lot_code = models.CharField(max_length=60, unique=True)
    quantity_kg = models.FloatField()
    received_at = models.DateTimeField(default=timezone.now)

class InventoryItem(models.Model):
    sku = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=GrainType.choices, default=GrainType.ARABICA)
    stock_kg = models.FloatField(default=0)
    min_stock_kg = models.FloatField(default=10)

class PurchaseOrder(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    supplier = models.CharField(max_length=120)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    qty_kg = models.FloatField()
    status = models.CharField(max_length=20, default='pending')

# --- Producción (Procesos y Lotes) ---
class ProcessStage(models.TextChoices):
    ROAST = 'roast', 'Tostado'
    GRIND = 'grind', 'Molido'
    PACK  = 'pack',  'Empaque'

class ProductionTask(models.Model):
    stage = models.CharField(max_length=20, choices=ProcessStage.choices)
    assigned_unit = models.CharField(max_length=120)  # p.ej. "Tostado 1"
    planned_kg = models.FloatField()
    progress = models.FloatField(default=0)  # 0..100
    created_at = models.DateTimeField(default=timezone.now)

class ProductBatch(models.Model):
    code = models.CharField(max_length=60, unique=True)
    coffee_type = models.CharField(max_length=20, choices=GrainType.choices)
    qty_kg = models.FloatField()
    cupping_score = models.FloatField(null=True, blank=True)  # control de calidad
    mfg_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateField()

# --- Pedidos y Distribución ---
class DeliverySpeed(models.TextChoices):
    FAST = 'fast', 'Rápida'
    ECON = 'economy', 'Económica'

class Order(models.Model):
    customer = models.CharField(max_length=120)  # distribuidor/tienda
    created_at = models.DateTimeField(default=timezone.now)
    delivery_speed = models.CharField(max_length=20, choices=DeliverySpeed.choices, default=DeliverySpeed.ECON)
    status = models.CharField(max_length=20, default='received')

class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    batch = models.ForeignKey(ProductBatch, on_delete=models.PROTECT)
    qty_kg = models.FloatField()

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    route = models.TextField(blank=True)         # ruta planificada
    shipped_at = models.DateTimeField(null=True, blank=True)
    received_confirmed = models.BooleanField(default=False)
