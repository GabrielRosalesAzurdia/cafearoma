from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.orders_dashboard, name='dashboard'),
    path('create/', views.create_order, name='create_order'),
    path('plan-distribution/<int:order_id>/', views.plan_distribution, name='plan_distribution'),
    path('create-shipment/<int:order_id>/', views.create_shipment, name='create_shipment'),
    path('shipment-status/<int:order_id>/', views.shipment_status, name='shipment_status'),
]