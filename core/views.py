from django.shortcuts import render
from inventory.models import InventoryItem
from production.models import ProductBatch
from orders.models import Order

def dashboard(request):
    # Estadísticas para el dashboard
    total_items = InventoryItem.objects.count()
    low_stock_items = [item for item in InventoryItem.objects.all() if item.needs_restock()]
    total_batches = ProductBatch.objects.count()
    active_orders = Order.objects.exclude(status__in=['DELIVERED', 'CANCELLED']).count()
    
    context = {
        'title': 'Dashboard - Café Aroma',
        'total_items': total_items,
        'low_stock_count': len(low_stock_items),
        'total_batches': total_batches,
        'active_orders': active_orders,
        'recent_batches': ProductBatch.objects.order_by('-mfg_date')[:3],
        'recent_orders': Order.objects.order_by('-created_at')[:3]
    }
    return render(request, 'core/dashboard.html', context)