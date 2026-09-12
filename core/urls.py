from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('accounts.urls')), # Mount accounts at root
]

handler403 = 'accounts.views.custom_403_view'