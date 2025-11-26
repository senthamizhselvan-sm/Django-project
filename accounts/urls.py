"""
URL patterns for accounts app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public routes
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    
    # Radiologist routes
    path('radiologist/dashboard/', views.radiologist_dashboard, name='radiologist_dashboard'),
    path('radiologist/analyze/<str:scan_id>/', views.analyze_scan, name='analyze_scan'),
    path('radiologist/reports/', views.view_completed_reports, name='view_completed_reports'),
    path('radiologist/pending/', views.view_pending_scans, name='view_pending_scans'),
    
    # PDF Generation route (accessible to both roles)
    path('generate-pdf/<str:scan_id>/', views.generate_pdf, name='generate_pdf'),
    
    # Technician routes
    path('technician/dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('technician/upload/', views.upload_scan, name='upload_scan'),
    path('technician/scans/', views.view_scans, name='view_scans'),
    path('technician/scan/<str:scan_id>/', views.view_scan_detail, name='view_scan_detail'),
    
    # Analytics Dashboard routes
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Analytics API endpoints (JSON responses for charts)
    path('api/daily-scans/', views.api_daily_scans, name='api_daily_scans'),
    path('api/scan-types/', views.api_scan_types, name='api_scan_types'),
    path('api/workload/', views.api_workload_distribution, name='api_workload'),
    path('api/heatmap/', views.api_heatmap_data, name='api_heatmap'),
    path('api/performance/', views.api_performance_chart, name='api_performance'),
]
