from django.urls import path
from . import views

urlpatterns = [
    path("seed-inventory/", views.seed_inventory),
    path("produce-batch/", views.produce_batch),
    path("create-combo/", views.create_combo),
    path("ship-order/", views.ship_order),
    path("inventario/", views.inventory_view, name="inventory"),
    path("lotes/", views.batches_view, name="batches"),
    path("pedidos/", views.orders_view, name="orders"),
]
