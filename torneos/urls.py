from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),                                       
    path('torneos/', views.lista_torneos_view, name='lista_torneos'),          
    path('inscribir/<int:torneo_id>/', views.inscribir_escuadra, name='inscribir_escuadra'),
    path('matchmaking/', views.matchmaking_view, name='matchmaking'),
    path('arbitraje/', views.panel_arbitraje, name='panel_arbitraje'),
    path('resolver-disputa/<int:disputa_id>/', views.resolver_disputa, name='resolver_disputa'),
    path('crear/', views.crear_torneo, name='crear_torneo'),
    path('intercarreras/', views.ranking_intercarreras_view, name='ranking_intercarreras'),
    path('validar-dae/<int:pk>/', views.validar_torneo_dae, name='validar_torneo_dae'),
]