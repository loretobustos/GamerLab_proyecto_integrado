from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),                                       
    path('torneos/', views.lista_torneos_view, name='lista_torneos'),           
    path('torneos/inscribir/<int:torneo_id>/', views.inscribir_torneo_view, name='inscribir_torneo'),
    path('matchmaking/', views.matchmaking_view, name='matchmaking'),
    path('arbitraje/', views.panel_arbitraje, name='panel_arbitraje'),
    path('resolver-disputa/<int:disputa_id>/', views.resolver_disputa, name='resolver_disputa'),
    path('crear/', views.crear_torneo, name='crear_torneo'),
    path('intercarreras/', views.ranking_intercarreras_view, name='ranking_intercarreras'),
    path('escuadra/', views.gestionar_escuadra_view, name='gestionar_escuadra'),
    path('invitaciones/', views.mis_invitaciones_view, name='mis_invitaciones'),
    path('invitaciones/aceptar/<int:invitacion_id>/', views.aceptar_invitacion_view, name='aceptar_invitacion'),
    path('buscar-jugadores/', views.buscar_jugadores_view, name='buscar_jugadores'),
    path('partida/<int:partida_id>/resultado/', views.registrar_resultado_view, name='registrar_resultado'),
    path('validar-dae/<int:pk>/', views.validar_torneo_dae, name='validar_torneo_dae'),
]