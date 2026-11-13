from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Torneo, Escuadra, Partida

def lista_torneos_view(request):
    """
    Lista los torneos activos e históricos de la sede (Inscripción y Cupos).
    """
    torneos = Torneo.objects.all()
    return render(request, 'torneos.html', {'torneos': torneos})

@login_required
def inscribir_escuadra_view(request, torneo_id):
    torneo = get_object_or_404(Torneo, pk=torneo_id)
    if request.method == 'POST':
        nombre_escuadra = request.POST.get('nombre_escuadra')
        # Verificar cupos disponibles (Potencia de 2)
        if torneo.escuadras.count() < torneo.cupos_maximos:
            Escuadra.objects.create(
                nombre_escuadra=nombre_escuadra,
                torneo=torneo,
                capitan=request.user
            )
        return redirect('lista_torneos')
    return redirect('lista_torneos')

def matchmaking_view(request):
    """
    Simulación de emparejamiento orientativo por ELO y modalidad intercarreras.
    """
    resultado_match = None
    if request.method == 'POST':
        elo_usuario = int(request.POST.get('elo', 1500))
        modo = request.POST.get('mode', 'Intercarrera mixto')
        
        # Lógica orientativa de emparejamiento por rango ELO (± 150 puntos)
        rango_min = elo_usuario - 150
        rango_max = elo_usuario + 150
        
        resultado_match = {
            'elo_buscado': elo_usuario,
            'rango': f"{rango_min} - {rango_max} ELO",
            'modo': modo,
            'estado': '¡Escuadra equilibrada encontrada con éxito para la sede!'
        }
        
    return render(request, 'matchmaking.html', {'resultado_match': resultado_match})