from django.urls import path
from . import views

urlpatterns = [
    path('', views.bazar_catalogo_view, name='bazar_catalogo'),
    path('solicitar/<int:publicacion_id>/', views.solicitar_canje_view, name='solicitar_canje'),
]