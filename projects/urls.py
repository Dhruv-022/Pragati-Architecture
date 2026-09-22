from django.urls import path
from . import views
from .views import data_overview_view, project_detail_view

app_name = 'projects'

urlpatterns = [
    path('explorer/', views.data_overview_view, name='data_overview'),
    path('explorer/<str:table_name>/', views.table_detail_view, name='table_detail'),
    path('project/<str:project_id>/', project_detail_view, name='project_detail'),
]
