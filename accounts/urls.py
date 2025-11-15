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
    path('radiologist/analyze/<int:scan_id>/', views.analyze_scan, name='analyze_scan'),
    path('radiologist/reports/', views.view_completed_reports, name='view_completed_reports'),
    path('radiologist/pending/', views.view_pending_scans, name='view_pending_scans'),
    
    # Technician routes
    path('technician/dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('technician/upload/', views.upload_scan, name='upload_scan'),
    path('technician/scans/', views.view_scans, name='view_scans'),
    path('technician/scan/<int:scan_id>/', views.view_scan_detail, name='view_scan_detail'),
]
