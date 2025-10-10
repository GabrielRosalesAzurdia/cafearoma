from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('consume-stock/', views.consume_stock, name='consume_stock'),
    path('add-product/', views.add_product_command, name='add_product'),
    path('undo/', views.undo_last_command, name='undo'),
    path('clear-history/', views.clear_command_history, name='clear_history'),
    path('download-report/', views.download_inventory_report, name='download_report'),
]