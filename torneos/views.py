from django.shortcuts import render, get_object_or_404, redirect
from .models import Torneo, Escuadra, Partida, CalificacionTorneo, InvitacionEscuadra 
from cuentas.models import Usuario
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse

@login_required
def ranking_intercarreras_view(request):
    # Validamos roles permitidos
    if request.user.rol not in ['Docente', 'Gestor', 'Administrador', 'DAE'] and not request.user.is_superuser:
        return HttpResponseForbidden("Acceso denegado: No tienes permisos para ver el ranking intercarreras.")
    
    # Validación opcional de parámetro de entrada (CP-INT-07 / RNF-04)
    id_carrera = request.GET.get('idCarrera')
    if id_carrera:
        try:
            id_carrera = int(id_carrera) # Si envían "abc" o inyección, lanza ValueError de forma segura
        except ValueError:
            return HttpResponse("Solicitud inválida (Bad Request): Parámetro no numérico.", status=400)

    return render(request, 'intercarreras.html')

def es_potencia_de_dos(n):
    """Verifica si un número es potencia de 2 (ej: 4, 8, 16, 32)."""
    return n > 0 and (n & (n - 1)) == 0


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
    user_rol = getattr(request.user, 'rol', None)
    if request.user.is_authenticated and (user_rol in ['Administrador', 'DAE'] or request.user.is_superuser):
        torneos = Torneo.objects.all()
    else:
        # Los jugadores solo ven torneos validados por el DAE
        torneos = Torneo.objects.filter(validado_dae=True)
    return render(request, 'torneos.html', {'torneos': torneos})


@login_required
def crear_torneo(request):
    user_rol = getattr(request.user, 'rol', None)
    if user_rol not in ['Administrador', 'DAE'] and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado: Solo la administración y DAE pueden crear torneos oficiales.')
        return redirect('/torneos/')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        juego = request.POST.get('juego')
        cupos_maximos = int(request.POST.get('cupos_maximos', 0))
        premio_creditos = request.POST.get('premio_creditos')
        
        # 1. Capturamos los datos del formulario de laboratorio (ej. L-3, fecha y hora)
        laboratorio_asignado = request.POST.get('laboratorio')
        fecha_seleccionada = request.POST.get('fecha_reserva')
        horario_seleccionado = request.POST.get('horario_reserva')

        # 2. --- VALIDACIÓN DE DOBLE ASIGNACIÓN DE LABORATORIO (RF-16 CP-INT-04) ---
        if laboratorio_asignado and fecha_seleccionada and horario_seleccionado:
            conflicto = Torneo.objects.filter(
                laboratorio=laboratorio_asignado, 
                fecha_reserva=fecha_seleccionada, 
                horario_reserva=horario_seleccionado
            ).exists()

            if conflicto:
                messages.error(request, "Espacio no disponible en ese horario.")
                return redirect('/torneos/')

        # 3. --- VALIDACIÓN DE POTENCIA DE 2 (4, 8, 16, 32, 64) ---
        if cupos_maximos <= 0 or not es_potencia_de_dos(cupos_maximos):
            messages.error(request, 'Error 400: La cantidad de cupos debe ser potencia de 2 (4, 8, 16 o 32) para generar el fixture.')
            return render(request, 'crear_torneo.html', {
                'error_cupos': True,
                'datos_previos': request.POST
            })

        # 4. Creación final del torneo incluyendo los datos de laboratorio
        Torneo.objects.create(
            nombre=nombre,
            juego=juego,
            cupos_maximos=cupos_maximos,
            premio_creditos=float(premio_creditos),
            laboratorio=laboratorio_asignado if laboratorio_asignado else None,
            fecha_reserva=fecha_seleccionada if fecha_seleccionada else None,
            horario_reserva=horario_seleccionado if horario_seleccionado else None
        )
        
        messages.success(request, f'Torneo institucional "{nombre}" publicado exitosamente.')
        return redirect('/torneos/')

    return render(request, 'crear_torneo.html')


@login_required
def validar_torneo_dae(request, pk):
    user_rol = getattr(request.user, 'rol', None)
    if user_rol != 'DAE' and not request.user.is_superuser:
        messages.error(request, 'Solo el personal DAE puede validar el espacio de los torneos.')
        return redirect('/torneos/')
        
    torneo = get_object_or_404(Torneo, pk=pk)
    torneo.validado_dae = True
    torneo.save()
    messages.success(request, f'Espacio validado por DAE. El torneo "{torneo.nombre}" ya está abierto para jugadores.')
    return redirect('/torneos/')


@login_required
def inscribir_escuadra(request, torneo_id):
    """
    Permite registrar una escuadra o inscripción individual en un torneo específico.
    """
    torneo = get_object_or_404(Torneo, pk=torneo_id, validado_dae=True)
    
    if request.method == 'POST':
        nombre_escuadra = request.POST.get('nombre_escuadra', '').strip()
        
        if not nombre_escuadra:
            nombre_escuadra = f"Individual - {request.user.username}"
        
        # Validar si el torneo ya alcanzó el límite máximo de cupos
        total_inscritos = torneo.escuadras_inscritas.count()
        if total_inscritos >= torneo.cupos_maximos:
            messages.error(request, f"El torneo '{torneo.nombre}' ya completó sus cupos máximos.")
            return redirect('/torneos/')
            
        # Verificar potencia de 2 en cupos máximos
        if not es_potencia_de_dos(torneo.cupos_maximos):
            messages.error(request, "Error administrativo: Los cupos máximos del torneo deben ser una potencia de 2.")
            return redirect('/torneos/')

        Escuadra.objects.create(
            nombre_escuadra=nombre_escuadra,
            torneo=torneo,
            capitan=request.user
        )
        
        messages.success(request, f"¡Inscripción confirmada en '{torneo.nombre}' como: {nombre_escuadra}!")
        return redirect('/torneos/')

    return redirect('/torneos/')


@login_required
def crear_equipo_view(request):
    """
    Permite a un estudiante crear un equipo, subir su logo e invitar jugadores (RF-12 / CP-HU03-04).
    """
    if request.method == 'POST':
        nombre_escuadra = request.POST.get('nombre_escuadra', '').strip()
        logo_file = request.FILES.get('logo')
        jugador_invitado_id = request.POST.get('jugador_id')

        if Escuadra.objects.filter(nombre_escuadra__iexact=nombre_escuadra).exists():
            messages.error(request, "El nombre del equipo ya está en uso.")
            return redirect('/crear-equipo/')

        # Crear el equipo con su capitán y logo
        nueva_escuadra = Escuadra.objects.create(
            nombre_escuadra=nombre_escuadra,
            capitan=request.user,
            logo=logo_file
        )

        # Registrar la invitación si seleccionaron a un jugador
        if jugador_invitado_id:
            jugador_obj = get_object_or_404(Usuario, id=jugador_invitado_id)
            InvitacionEscuadra.objects.create(
                escuadra=nueva_escuadra,
                jugador_invitado=jugador_obj
            )
            messages.success(request, f"¡Equipo '{nombre_escuadra}' creado e invitación enviada a {jugador_obj.username}!")
        else:
            messages.success(request, f"¡Equipo '{nombre_escuadra}' creado exitosamente!")

        return redirect('/torneos/')

    return render(request, 'crear_equipo.html')


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
    if getattr(request.user, 'rol', None) != 'DAE' and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')
    
    context = {
        'mensaje': 'Panel de Gestión DAE - Premios y Beneficios INACAP Maipú'
    }
    return render(request, 'panel_dae.html', context)


@login_required
def panel_arbitraje(request):
    """
    Sala de arbitraje administrativo y DAE para resolución de disputas (HU-02).
    """
    user_rol = getattr(request.user, 'rol', None)
    if user_rol not in ['Administrador', 'DAE'] and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado: Solo la administración y DAE pueden gestionar el arbitraje.')
        return redirect('/torneos/')

    disputas = Partida.objects.filter(estado='EnDisputa')

    return render(request, 'arbitraje.html', {'disputas': disputas})


@login_required
def resolver_disputa(request, disputa_id):
    """
    Procesa el fallo del árbitro (Admin o DAE), cierra la disputa y actualiza el estado de la partida.
    """
    user_rol = getattr(request.user, 'rol', None)
    if user_rol not in ['Administrador', 'DAE'] and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado: Solo la administración y DAE pueden emitir fallos arbitrales.')
        return redirect('/torneos/')

    partida = get_object_or_404(Partida, id_partida=disputa_id)
    
    if request.method == 'POST':
        ganador_id = request.POST.get('ganador_id')
        dictamen = request.POST.get('dictamen_arbitro')

        ganador_escuadra = get_object_or_404(Escuadra, id_escuadra=ganador_id)
        
        partida.estado = 'Finalizada'
        partida.save()

        messages.success(request, f'Partida #{partida.id_partida} resuelta con éxito. Ganador: {ganador_escuadra.nombre_escuadra}. Dictamen: {dictamen}')
        return redirect('/arbitraje/')

    return redirect('/arbitraje/')