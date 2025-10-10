from django.shortcuts import render, redirect
from django.contrib import messages
from .facade import ProductionFacade
from .models import ProductionTask, ProductBatch
from core.inventory_manager import InventoryManager
from inventory.repositories import DjangoInventoryRepo
from core.reports import ReportGenerator

# Inicializar facade
repo = DjangoInventoryRepo()
inv_manager = InventoryManager(repo)
production_facade = ProductionFacade(inv_manager)

def production_dashboard(request):
    tasks = ProductionTask.objects.all().order_by('-created_at')
    batches = ProductBatch.objects.all().order_by('-mfg_date')
    
    context = {
        'tasks': tasks,
        'batches': batches,
        'process_stages': ProductionTask._meta.get_field('stage').choices
    }
    return render(request, 'production/dashboard.html', context)

def start_production(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        kg = float(request.POST.get('kg', 0))
        kind = request.POST.get('kind', 'arabica')
        coffee_type = request.POST.get('coffee_type', 'AR')
        
        result = production_facade.start_production(sku, kg, kind, coffee_type)
        
        if result['success']:
            messages.success(request, result['message'])
            if 'production_task' in result:
                messages.info(request, f'📦 Tarea #{result["production_task"].id} iniciada')
                messages.info(request, f'⚙️ Estado actual: {result["production_task"].get_stage_display()}')
        else:
            error_msg = result.get('error', 'Error desconocido')
            messages.error(request, f'❌ Error al iniciar producción: {error_msg}')
        
        return redirect('production:dashboard')

def advance_stage(request, task_id):
    """Avanza una tarea de producción a la siguiente etapa"""
    result = production_facade.advance_production_stage(task_id)
    
    if result['success']:
        messages.success(request, result['message'])
        if 'product_batch' in result:
            messages.success(request, f'📦 Lote creado: {result["product_batch"].code}')
    else:
        messages.error(request, f'❌ Error: {result["error"]}')
    
    return redirect('production:dashboard')

def task_detail(request, task_id):
    """Muestra el detalle de una tarea de producción"""
    status = production_facade.get_production_status(task_id)
    
    if 'error' in status:
        messages.error(request, status['error'])
        return redirect('production:dashboard')
    
    context = {
        'task_id': task_id,
        'status': status
    }
    return render(request, 'production/task_detail.html', context)

def production_report(request):
    report = production_facade.generate_production_report()
    context = {
        'report': report.split('\n')
    }
    return render(request, 'production/report.html', context)

def batch_detail(request, batch_code):
    try:
        batch = ProductBatch.objects.get(code=batch_code)
        context = {
            'batch': batch
        }
        return render(request, 'production/batch_detail.html', context)
    except ProductBatch.DoesNotExist:
        messages.error(request, f'Lote {batch_code} no encontrado')
        return redirect('production:dashboard')

def download_production_report(request, format_type='pdf'):
    """Descarga reporte de producción en formato PDF o CSV"""
    tasks = ProductionTask.objects.all().order_by('-created_at')
    batches = ProductBatch.objects.all().order_by('-mfg_date')
    
    if format_type == 'csv':
        return ReportGenerator.generate_production_csv(tasks, batches)
    else:  # pdf por defecto
        return ReportGenerator.generate_production_pdf(tasks, batches)

def production_analytics(request):
    """Vista de análisis y estadísticas de producción"""
    tasks = ProductionTask.objects.all()
    batches = ProductBatch.objects.all()
    
    # Estadísticas
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(stage='CO').count()
    in_progress_tasks = total_tasks - completed_tasks
    
    total_coffee_kg = sum(batch.qty_kg for batch in batches)
    
    # Tareas por etapa
    stages_data = {}
    for stage_code, stage_name in ProductionTask._meta.get_field('stage').choices:
        stages_data[stage_name] = tasks.filter(stage=stage_code).count()
    
    # Café por tipo
    coffee_types_data = {}
    for type_code, type_name in ProductBatch._meta.get_field('coffee_type').choices:
        type_batches = batches.filter(coffee_type=type_code)
        coffee_types_data[type_name] = {
            'count': type_batches.count(),
            'total_kg': sum(batch.qty_kg for batch in type_batches),
            'avg_score': sum(batch.cupping_score for batch in type_batches if batch.cupping_score) / type_batches.count() if type_batches.count() > 0 else 0
        }
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'total_coffee_kg': total_coffee_kg,
        'stages_data': stages_data,
        'coffee_types_data': coffee_types_data,
        'batches': batches[:10]  # Últimos 10 lotes
    }
    
    return render(request, 'production/analytics.html', context)