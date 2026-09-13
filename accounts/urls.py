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

    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    path('admin-panel/manage-users/', views.manage_users_view, name='manage_users'),
    path('admin-panel/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-panel/projects/', views.project_directory_view, name='project_directory'),

    path('workspace/monitoring/', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('workspace/project/<int:project_id>/update-status/', views.update_project_status, name='update_project_status'),
    path('workspace/project/<int:project_id>/flag-investigation/', views.flag_project_for_investigation, name='flag_project_for_investigation'),
]