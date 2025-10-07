from django.db import models
from core.models import DeliverySpeed

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'En proceso'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    id = models.AutoField(primary_key=True)
    customer = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_speed = models.CharField(max_length=2, choices=DeliverySpeed.choices)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    def confirm_received(self):
        self.status = 'DELIVERED'
        self.save()
    
    def __str__(self):
        return f"Order {self.id} - {self.customer}"

class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    product_batch = models.ForeignKey('production.ProductBatch', on_delete=models.CASCADE)
    qty_kg = models.FloatField()
    
    def __str__(self):
        return f"Line {self.id} - Order {self.order.id}"

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    route = models.CharField(max_length=200)
    shipped_at = models.DateTimeField(auto_now_add=True)
    received_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Delivery for Order {self.order.id}"