# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Core Authentication & Dynamic Workspace Routing
    path('workspace/', views.workspace_redirect_view, name='workspace_redirect'),
    path('login/', views.smart_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.logout_view, name='admin_logout'),
    path('investigation/dashboard/', views.mospi_admin_dashboard),  # Safety alias to redirect legacy clicks
    path('monitoring/dashboard/', views.mospi_admin_dashboard),     # Safety alias to redirect legacy clicks

    # Valid Role Dashboards
    path('admin-panel/', views.mospi_admin_dashboard, name='admin_dashboard'),
    path('mospi/national-dashboard/', views.mospi_admin_dashboard, name='mospi_dashboard'),
    path('mp/dashboard/', views.mp_dashboard, name='mp_dashboard'),
    path('district/dashboard/', views.district_dashboard, name='district_dashboard'),
    
    # Detail Views & Actions
    path('mospi/state/<str:state_name>/projects/', views.state_projects_detail_view, name='state_projects_detail'),
    path('admin-panel/projects/', views.project_directory_view, name='project_directory'),
    path('admin-panel/users/create/', views.create_user, name='create_user'),
    path('admin-panel/users/manage/', views.manage_users_view, name='manage_users'),
    path('admin-panel/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('mp/district/<str:district_name>/alerts/', views.mp_district_alerts_view, name='mp_district_alerts'),
    path('mp/district/<str:district_name>/works/<str:status_type>/', views.mp_district_works_view, name='mp_district_works'),
]