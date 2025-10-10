from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('', views.production_dashboard, name='dashboard'),
    path('start/', views.start_production, name='start_production'),
    path('advance/<int:task_id>/', views.advance_stage, name='advance_stage'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('report/', views.production_report, name='report'),
    path('analytics/', views.production_analytics, name='analytics'),
    path('download-report/<str:format_type>/', views.download_production_report, name='download_report'),
    path('batch/<str:batch_code>/', views.batch_detail, name='batch_detail'),
]