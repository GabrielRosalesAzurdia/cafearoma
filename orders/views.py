from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, Delivery
from .strategies import ContextoDeDistribucion, DistribucionRapida, DistribucionEconomica
from .adapters import LogisticsAdapterFactory

def orders_dashboard(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Calcular estadísticas
    total_orders = orders.count()
    pending_orders = orders.filter(status='PENDING').count()
    processing_orders = orders.filter(status='PROCESSING').count()
    shipped_orders = orders.filter(status='SHIPPED').count()
    delivered_orders = orders.filter(status='DELIVERED').count()
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'orders/dashboard.html', context)


def plan_distribution(request, order_id):
    """Planifica la ruta de distribución para una orden"""
    try:
        order = Order.objects.get(id=order_id)
        contexto = ContextoDeDistribucion()
        
        # Seleccionar estrategia basada en la velocidad de entrega
        if order.delivery_speed == 'RA':
            contexto.set_strategy(DistribucionRapida())
            strategy_name = "Distribución Rápida"
        else:
            contexto.set_strategy(DistribucionEconomica())
            strategy_name = "Distribución Económica"
        
        # Ejecutar la estrategia
        route_plan = contexto.execute_strategy(order)
        
        # Mostrar mensaje de éxito
        messages.success(request, f'🗺️ {route_plan}')
        messages.info(request, f'📦 Orden #{order.id} - Cliente: {order.customer}')
        messages.info(request, f'⚡ Estrategia utilizada: {strategy_name}')
        
    except Order.DoesNotExist:
        messages.error(request, f'❌ Error: Orden #{order_id} no encontrada')
    except Exception as e:
        messages.error(request, f'❌ Error en planificación: {str(e)}')
    
    return redirect('orders:dashboard')

def create_order(request):
    if request.method == 'POST':
        customer = request.POST.get('customer')
        delivery_speed = request.POST.get('delivery_speed', 'EC')
        
        order = Order.objects.create(
            customer=customer,
            delivery_speed=delivery_speed
        )
        
        messages.success(request, f'✅ Orden {order.id} creada para {customer}')
        return redirect('orders:dashboard')

def create_shipment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Usar el adapter para integrar con el API externo
    adapter_factory = LogisticsAdapterFactory()
    adapter = adapter_factory.create_adapter('default')
    
    # Determinar la velocidad
    speed = 'rapida' if order.delivery_speed == 'RA' else 'economica'
    
    result = adapter.create_shipment(order.id, speed)
    
    if result['success']:
        # Crear registro de envío
        delivery = Delivery.objects.create(
            order=order,
            route=result['carrier'],
            received_confirmed=False
        )
        
        order.status = 'SHIPPED'
        order.save()
        
        messages.success(request, result['message'])
        messages.info(request, f'📦 Carrier: {result["carrier"]}')
        messages.info(request, f'⏱️ Tiempo estimado: {result["estimated_days"]} días')
    else:
        messages.error(request, result['error'])
    
    return redirect('orders:dashboard')

def shipment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    try:
        delivery = Delivery.objects.get(order=order)
        adapter_factory = LogisticsAdapterFactory()
        adapter = adapter_factory.create_adapter('default')
        
        # Simulamos un número de tracking para demostración
        tracking_number = f"TRACK_{order.id}_{order.delivery_speed}"
        
        result = adapter.get_shipment_status(tracking_number)
        
        if result['success']:
            context = {
                'order': order,
                'delivery': delivery,
                'shipment_status': result['status']
            }
            return render(request, 'orders/shipment_status.html', context)
        else:
            messages.error(request, result['error'])
            return redirect('orders:dashboard')
            
    except Delivery.DoesNotExist:
        messages.error(request, 'No se encontró información de envío para esta orden')
        return redirect('orders:dashboard')