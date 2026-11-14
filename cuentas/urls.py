from django.urls import path
from . import views
from .views import perfil_billetera_view
from .views import (
    GamerLabPasswordResetView,
    GamerLabPasswordResetDoneView,
    GamerLabPasswordResetConfirmView,
    GamerLabPasswordResetCompleteView
)

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('panel-dae/', views.panel_dae_view, name='panel_dae'),
    path('perfil/', perfil_billetera_view, name='perfil_billetera'),
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'), 
    path('password_reset/', GamerLabPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', GamerLabPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', GamerLabPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', GamerLabPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
