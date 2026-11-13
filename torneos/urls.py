from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_torneos_view, name='lista_torneos'),
    path('inscribir/<int:torneo_id>/', views.inscribir_escuadra_view, name='inscribir_escuadra'),
    path('matchmaking/', views.matchmaking_view, name='matchmaking'),
]