from django.shortcuts import render, get_object_or_404, redirect
from .models import Torneo, Escuadra
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def es_potencia_de_dos(n):
    """Verifica si un número es potencia de 2 (ej: 4, 8, 16, 32)."""
    return n > 0 and (n & (n - 1)) == 0

def inscribir_escuadra(request, torneo_pk):
    torneo = get_object_or_404(Torneo, pk=torneo_pk)
    
    if request.method == 'POST':
        nombre_escuadra = request.POST.get('nombre_escuadra')
        
        # Opcional: Validar si el torneo ya alcanzó el límite máximo de cupos permitidos
        total_inscritos = torneo.escuadras.count() # o el nombre de tu related_name
        
        if total_inscritos >= torneo.cupos_maximos:
            messages.error(request, f"El torneo '{torneo.nombre}' ya completó sus cupos máximos.")
            return redirect('lista_torneos')
            
        # Validación de potencia de 2 (si el modelo o las bases exigen potencias de 2 para el fixture)
        # Puedes aplicarlo para verificar los cupos máximos configurados por el administrador:
        if not es_potencia_de_dos(torneo.cupos_maximos):
            messages.error(request, "Error administrativo: Los cupos máximos del torneo deben ser una potencia de 2 (8, 16, 32).")
            return redirect('lista_torneos')

        # Crear la escuadra vinculada al torneo y al usuario
        Escuadra.objects.create(
            torneo=torneo,
            nombre=nombre_escuadra,
            capitan=request.user,
            estado='Inscrito'
        )
        
        messages.success(request, f"¡Escuadra '{nombre_escuadra}' inscrita con éxito en el torneo!")
        return redirect('lista_torneos')

    return redirect('lista_torneos')
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


@login_required
def panel_dae_view(request):
    """
    Panel exclusivo para el rol DAE / Curricular para la entrega y validación de premios.
    """
    if request.user.rol != 'DAE' and not request.user.is_superuser:
        return redirect('home')
    
    # Contexto para la gestión institucional de premios y beneficios de la sede
    context = {
        'mensaje': 'Panel de Gestión DAE - Premios y Beneficios INACAP Maipú'
    }
    return render(request, 'panel_dae.html', context)