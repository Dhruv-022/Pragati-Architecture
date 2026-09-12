# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Point 'login/' directly to smart_login_view
    path('login/', views.smart_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Control Center (System Admin)
    path('control-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('users/create/', views.create_user, name='create_user'),

    # Operational Dashboards
    path('district/dashboard/', views.district_dashboard, name='district_dashboard'),
    path('monitoring/dashboard/', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('investigation/dashboard/', views.investigation_dashboard, name='investigation_dashboard'),
]