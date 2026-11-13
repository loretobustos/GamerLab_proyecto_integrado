from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Torneo, Escuadra

def home_view(request):
    """
    Vista para la página de inicio (Dashboard principal de GamerLab).
    """
    torneos_destacados = Torneo.objects.all()[:3]
    return render(request, 'home.html', {'torneos_destacados': torneos_destacados})


def lista_torneos_view(request):
    """
    Muestra la lista de todos los torneos activos en la plataforma.
    """
    torneos = Torneo.objects.all()
    return render(request, 'torneos.html', {'torneos': torneos})


@login_required
def inscribir_escuadra_view(request, torneo_id):
    """
    Permite a un usuario registrar su escuadra en un torneo específico.
    """
    torneo = get_object_or_404(Torneo, pk=torneo_id)
    
    if request.method == 'POST':
        nombre_escuadra = request.POST.get('nombre_escuadra')
        
        if nombre_escuadra:
            # Crear la escuadra vinculada al usuario logueado como capitán y al torneo
            Escuadra.objects.create(
                nombre_escuadra=nombre_escuadra,
                torneo=torneo,
                capitan=request.user
            )
            return redirect('lista_torneos')
            
    return render(request, 'inscribir_escuadra.html', {'torneo': torneo})


@login_required
def matchmaking_view(request):
    """
    Panel de emparejamientos y matchmaking para los torneos.
    """
    torneos = Torneo.objects.all()
    return render(request, 'matchmaking.html', {'torneos': torneos})