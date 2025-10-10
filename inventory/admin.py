from django.contrib import admin
from .models import RawGrain, InventoryItem, PurchaseOrder

@admin.register(RawGrain)
class RawGrainAdmin(admin.ModelAdmin):
    list_display = ['lot_code', 'type', 'supplier', 'quantity_kg', 'received_at']
    list_filter = ['type', 'supplier']
    search_fields = ['lot_code', 'supplier']

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'type', 'stock_kg', 'min_stock_kg']
    list_filter = ['type']
    search_fields = ['sku', 'name']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'qty_kg', 'status', 'created_at']
    list_filter = ['status', 'supplier']
    search_fields = ['supplier']