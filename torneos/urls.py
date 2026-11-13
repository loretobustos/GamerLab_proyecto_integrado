from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),                                   # La raíz ahora es el Inicio
    path('torneos/', views.lista_torneos_view, name='lista_torneos'),          # La sección de torneos separada
    path('inscribir/<int:torneo_id>/', views.inscribir_escuadra_view, name='inscribir_escuadra'),
    path('matchmaking/', views.matchmaking_view, name='matchmaking'),
]