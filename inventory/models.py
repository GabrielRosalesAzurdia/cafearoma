from django.db import models
from core.models import GrainType

class RawGrain(models.Model):
    supplier = models.CharField(max_length=200)
    type = models.CharField(max_length=2, choices=GrainType.choices)
    origin = models.CharField(max_length=100)
    lot_code = models.CharField(max_length=50, unique=True)
    quantity_kg = models.FloatField()
    received_at = models.DateTimeField(auto_now_add=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.lot_code} - {self.get_type_display()}"

class InventoryItem(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=2, choices=GrainType.choices)
    stock_kg = models.FloatField(default=0)
    min_stock_kg = models.FloatField(default=10)
    
    def update_stock(self, kg: float):
        self.stock_kg += kg
        self.save()
        
    def needs_restock(self):
        return self.stock_kg <= self.min_stock_kg
        
    def __str__(self):
        return f"{self.sku} - {self.name}"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('ORDERED', 'Ordenado'),
        ('RECEIVED', 'Recibido'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    supplier = models.CharField(max_length=200)
    qty_kg = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"PO-{self.id} - {self.supplier}"