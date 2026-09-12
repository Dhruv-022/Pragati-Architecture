from django.urls import path
from . import views

# accounts/urls.py

urlpatterns = [
    path('login/', views.smart_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.logout_view, name='admin_logout'),

    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/create/', views.create_user, name='create_user'),

    path('district/dashboard/', views.district_dashboard, name='district_dashboard'),
    path('monitoring/dashboard/', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('investigation/dashboard/', views.investigation_dashboard, name='investigation_dashboard'),
]