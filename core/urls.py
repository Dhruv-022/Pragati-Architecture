from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include('accounts.urls')),
]
handler403 = 'accounts.views.custom_403_view'