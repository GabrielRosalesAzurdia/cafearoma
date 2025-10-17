from django.shortcuts import render, redirect
from django.contrib import messages
from core.factories import ComboFactoryCreator, ProductFactory

def combos_dashboard(request):
    """Dashboard para gestión de combos"""
    combo_types = ComboFactoryCreator.get_available_combo_types()
    
    context = {
        'combo_types': combo_types,
        'title': 'Gestión de Combos'
    }
    return render(request, 'products/dashboard.html', context)

def create_combo(request):
    """Crear un nuevo combo usando Abstract Factory"""
    if request.method == 'POST':
        combo_level = request.POST.get('combo_level')
        coffee_type = request.POST.get('coffee_type')
        coffee_weight = float(request.POST.get('coffee_weight', 0.25))
        
        try:
            # Usar el Abstract Factory para crear el combo
            factory = ComboFactoryCreator.create_factory(combo_level)
            combo = factory.create_combo(coffee_type, coffee_weight)
            
            # Mostrar información del combo creado
            messages.success(request, f'✅ Combo {factory.get_combo_type()} creado exitosamente!')
            messages.info(request, f'🎁 {combo.combo_name}')
            messages.info(request, f'☕ {combo.coffee.label()}')
            messages.info(request, f'🍵 {combo.mug}')
            messages.info(request, f'⏳ {combo.filter}')
            messages.info(request, f'💰 Precio total: ${combo.get_total_price():.2f}')
            
        except Exception as e:
            messages.error(request, f'❌ Error al crear combo: {str(e)}')
        
        return redirect('products:combos_dashboard')
    
    return redirect('products:dashboard')

def combo_catalog(request):
    """Mostrar catálogo de todos los combos disponibles"""
    combo_types = ComboFactoryCreator.get_available_combo_types()
    coffee_types = ['arabica', 'robusta', 'blend']
    
    # Crear ejemplos de cada tipo de combo
    combos = []
    for combo_type in combo_types:
        for coffee_type in coffee_types:
            try:
                factory = ComboFactoryCreator.create_factory(combo_type['value'])
                combo = factory.create_combo(coffee_type, 0.25)  # 250g por defecto
                combos.append({
                    'combo': combo,
                    'type_info': combo_type,
                    'coffee_type': coffee_type
                })
            except Exception as e:
                print(f"Error creando combo: {e}")
    
    context = {
        'combos': combos,
        'title': 'Catálogo de Combos'
    }
    return render(request, 'products/combo_catalog.html', context)