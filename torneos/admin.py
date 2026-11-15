from django.contrib import admin
from .models import Torneo, Escuadra, Partida, CalificacionTorneo, InvitacionEscuadra

admin.site.register(Torneo)
admin.site.register(Escuadra)
admin.site.register(Partida)  
admin.site.register(CalificacionTorneo)
admin.site.register(InvitacionEscuadra)