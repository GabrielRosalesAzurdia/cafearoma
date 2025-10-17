from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('combos/', views.combos_dashboard, name='combos_dashboard'),
    path('combos/create/', views.create_combo, name='create_combo'),
    path('combos/catalog/', views.combo_catalog, name='combo_catalog'),
    # Agrega aquí otras URLs de products si las tienes
]