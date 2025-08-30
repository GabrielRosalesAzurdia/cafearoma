from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models import InventoryItem, Order, Delivery, ProductBatch
from core.services.patterns import (
    InventoryManager, DjangoInventoryRepo, DefaultComboFactory, ProviderAdapter, ExternalLogisticsAPI
)
from core.services.facade import run_demo_production

@csrf_exempt
@require_POST
def seed_inventory(request):
    item, _ = InventoryItem.objects.get_or_create(
        sku="GR-AR-001",
        defaults=dict(name="Grano Arábica Base", type='arabica', stock_kg=50, min_stock_kg=10)
    )
    return JsonResponse({"sku": item.sku, "stock_kg": item.stock_kg})

@csrf_exempt
@require_POST
def produce_batch(request):
    executed, batch, item = run_demo_production(sku="GR-AR-001", kg=5, kind='arabica')
    return JsonResponse({
        "process": executed,
        "batch": batch.code,
        "new_stock_kg": item.stock_kg
    })

@csrf_exempt
@require_POST
def create_combo(request):
    factory = DefaultComboFactory()
    combo = factory.create_combo('arabica', 1.0)
    return JsonResponse({
        "combo": {
            "coffee": combo.coffee.label(),
            "mug": combo.mug.design,
            "filter": combo.filter.size
        }
    })

@csrf_exempt
@require_POST
def ship_order(request):
    # pedido mínimo para demo
    order = Order.objects.create(customer="Distribuidor X", delivery_speed='fast')
    delivery = Delivery.objects.create(order=order)
    adapter = ProviderAdapter(ExternalLogisticsAPI())
    external_id = adapter.create_shipment(order.id, speed=order.delivery_speed)
    delivery.route = f"Ruta externa {external_id}"
    delivery.save()
    return JsonResponse({
        "order_id": order.id,
        "external_shipment": external_id,
        "route": delivery.route
    })

from django.shortcuts import render

def inventory_view(request):
    items = InventoryItem.objects.all()
    return render(request, "core/inventory.html", {"items": items})

def batches_view(request):
    batches = ProductBatch.objects.all()
    return render(request, "core/batches.html", {"batches": batches})

def orders_view(request):
    orders = Order.objects.all()
    return render(request, "core/orders.html", {"orders": orders})
