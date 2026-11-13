"""
URL configuration for gamerlab_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Página de inicio principal (Carga el index.html de tu compañero)[cite: 1]
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Rutas de las aplicaciones de GamerLab
    path('cuentas/', include('cuentas.urls')),
    path('torneos/', include('torneos.urls')),
    path('arbitraje/', include('arbitraje.urls')),
    path('bazar/', include('bazar.urls')),
]