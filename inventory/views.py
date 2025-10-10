from django.shortcuts import render, redirect
from django.contrib import messages
from .models import InventoryItem, RawGrain
from .repositories import DjangoInventoryRepo
from .commands import CommandInvoker, AgregarStockCommand, ConsumirStockCommand, AgregarProductoCommand
from core.reports import ReportGenerator  # Asegúrate de importar ReportGenerator

# Inicializar repositorio
repo = DjangoInventoryRepo()

def inventory_dashboard(request):
    items = InventoryItem.objects.all()
    raw_grains = RawGrain.objects.all()[:5]
    
    # Inicializar CommandInvoker con la request
    command_invoker = CommandInvoker(request)
    
    # Verificar stock bajo
    low_stock_items = []
    for item in items:
        if item.needs_restock():
            low_stock_items.append(item)
    
    context = {
        'items': items,
        'raw_grains': raw_grains,
        'low_stock_items': low_stock_items,
        'command_history': command_invoker.get_history()
    }
    return render(request, 'inventory/dashboard.html', context)

def add_stock(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        kg = float(request.POST.get('kg', 0))
        
        # Usar CommandInvoker con la request
        command_invoker = CommandInvoker(request)
        command = AgregarStockCommand(repo, sku, kg)
        
        try:
            result = command_invoker.execute_command(command)
            messages.success(request, f'✅ {result}')
        except Exception as e:
            messages.error(request, f'❌ Error: {e}')
        
        return redirect('inventory:dashboard')

def consume_stock(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        kg = float(request.POST.get('kg', 0))
        
        # Usar CommandInvoker con la request
        command_invoker = CommandInvoker(request)
        command = ConsumirStockCommand(repo, sku, kg)
        
        try:
            result = command_invoker.execute_command(command)
            messages.success(request, f'✅ {result}')
        except Exception as e:
            messages.error(request, f'❌ Error: {e}')
        
        return redirect('inventory:dashboard')

def add_product_command(request):
    if request.method == 'POST':
        item_data = {
            'sku': request.POST.get('sku'),
            'name': request.POST.get('name'),
            'type': request.POST.get('type'),
            'stock_kg': float(request.POST.get('stock_kg', 0)),
            'min_stock_kg': float(request.POST.get('min_stock_kg', 10))
        }
        
        # Usar CommandInvoker con la request
        command_invoker = CommandInvoker(request)
        command = AgregarProductoCommand(repo, item_data)
        
        try:
            result = command_invoker.execute_command(command)
            messages.success(request, f'✅ {result}')
        except Exception as e:
            messages.error(request, f'❌ Error: {e}')
        
        return redirect('inventory:dashboard')

def undo_last_command(request):
    # Usar CommandInvoker con la request
    command_invoker = CommandInvoker(request)
    result = command_invoker.undo_last()
    messages.info(request, f'↩️ {result}')
    return redirect('inventory:dashboard')

def clear_command_history(request):
    """Nueva vista para limpiar el historial de comandos"""
    command_invoker = CommandInvoker(request)
    command_invoker.clear_history()
    messages.info(request, '🗑️ Historial de comandos limpiado')
    return redirect('inventory:dashboard')

# AÑADIR ESTA FUNCIÓN FALTANTE
def download_inventory_report(request):
    """Descarga reporte de inventario en formato CSV"""
    items = InventoryItem.objects.all()
    raw_grains = RawGrain.objects.all()
    
    return ReportGenerator.generate_inventory_csv(items, raw_grains)