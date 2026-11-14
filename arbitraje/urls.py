from django.urls import path
from . import views

urlpatterns = [
    path('', views.sala_disputas_view, name='sala_disputas'),
    path('resolver/<int:disputa_id>/', views.resolver_disputa_view, name='resolver_disputa'),
]