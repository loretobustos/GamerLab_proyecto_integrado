from django.urls import path
from . import views
from .views import mis_canjes_view

urlpatterns = [
    path('', views.bazar_catalogo_view, name='bazar_catalogo'),
    path('publicar/', views.crear_publicacion_bazar_view, name='crear_publicacion'), 
    path('canjear/<int:publicacion_id>/', views.solicitar_canje_view, name='solicitar_canje'),
    path('admin-escrow/', views.panel_admin_escrow_view, name='panel_admin_escrow'),
    path('admin-escrow/aprobar/<int:transaccion_id>/', views.aprobar_canje_admin_view, name='aprobar_canje_admin'),
    path('bazar/mis-canjes/', mis_canjes_view, name='mis_canjes'),
]
