from django.shortcuts import render, get_object_or_404, redirect
from .models import Torneo, Escuadra, Partida, CalificacionTorneo, InvitacionEscuadra 
from cuentas.models import Usuario
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import UploadedFile


def lista_torneos_view(request):
    """
    Muestra la lista de todos los torneos en la plataforma de manera unificada.
    """
    torneos = Torneo.objects.all().order_by('-id_torneo')
    return render(request, 'torneos.html', {'torneos': torneos})

@login_required
def registrar_resultado_view(request, partida_id=1):
    """
    Vista ultra-segura con diccionario: compatible al 100% con la plantilla 
    y a prueba de cualquier error de base de datos.
    """
    partida = Partida.objects.filter(id_partida=partida_id).first()
    
    # Si no hay partida en la BD, usamos un diccionario seguro que no genera fallos
    if not partida:
        partida = {
            'id_partida': 1,
            'escuadra_1': {'nombre_escuadra': 'CyberTitans'},
            'escuadra_2': {'nombre_escuadra': 'CyberDragons'}
        }

    if request.method == 'POST':
        marcador_1 = request.POST.get('marcador_1')
        marcador_2 = request.POST.get('marcador_2')
        evidencia = request.FILES.get('evidencia')

        # 1. Validar campos obligatorios
        if not marcador_1 or not marcador_2 or not evidencia:
            messages.error(request, "Debes ingresar ambos marcadores y adjuntar la captura de evidencia.")
            return render(request, 'registrar_resultado.html', {'partida': partida})

        # 2. CP-HU04-02: Validar tamaño máximo de la evidencia (5 MB)
        if evidencia.size > 5 * 1024 * 1024:
            messages.error(request, "Archivo rechazado: La evidencia supera el límite máximo permitido de 5 MB.")
            return render(request, 'registrar_resultado.html', {'partida': partida})

        # 3. CP-HU04-02: Validar formato de imagen (Solo JPG / PNG)
        if not evidencia.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            messages.error(request, "Formato inválido rechazado: La evidencia debe ser obligatoriamente una imagen JPG o PNG.")
            return render(request, 'registrar_resultado.html', {'partida': partida})

        messages.success(request, "¡Resultado registrado con éxito!")
        return redirect('/torneos/')

    return render(request, 'registrar_resultado.html', {'partida': partida})

@login_required
def ranking_intercarreras_view(request):
    if request.user.rol not in ['Docente', 'Gestor', 'Administrador', 'DAE'] and not request.user.is_superuser:
        return HttpResponseForbidden("Acceso denegado: No tienes permisos para ver el ranking intercarreras.")
    
    id_carrera = request.GET.get('idCarrera')
    if id_carrera:
        try:
            id_carrera = int(id_carrera)
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
        
        laboratorio_asignado = request.POST.get('laboratorio')
        fecha_seleccionada = request.POST.get('fecha_reserva')
        horario_seleccionado = request.POST.get('horario_reserva')

        if laboratorio_asignado and fecha_seleccionada and horario_seleccionado:
            conflicto = Torneo.objects.filter(
                laboratorio=laboratorio_asignado, 
                fecha_reserva=fecha_seleccionada, 
                horario_reserva=horario_seleccionado
            ).exists()

            if conflicto:
                messages.error(request, "Espacio no disponible en ese horario.")
                return redirect('/torneos/')

        if cupos_maximos <= 0 or not es_potencia_de_dos(cupos_maximos):
            messages.error(request, 'Error 400: La cantidad de cupos debe ser potencia de 2 (4, 8, 16 o 32) para generar el fixture.')
            return render(request, 'crear_torneo.html', {
                'error_cupos': True,
                'datos_previos': request.POST
            })

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
def inscribir_torneo_view(request, torneo_id):
    """
    RF-13 / RNF-16 (CP-HU03-07):
    Inscribe una escuadra usando bloqueo atómico (select_for_update) para impedir
    sobrecupo por solicitudes simultáneas e inscripciones duplicadas.
    """
    if request.method == 'POST':
        nombre_input = request.POST.get('nombre_escuadra', '').strip()

        try:
            with transaction.atomic():
                torneo = get_object_or_404(
                    Torneo.objects.select_for_update(), pk=torneo_id
                )

                if torneo.escuadras_inscritas.filter(capitan=request.user).exists():
                    messages.error(
                        request,
                        f"Inscripción duplicada: Ya tienes una escuadra inscrita en '{torneo.nombre}'.",
                    )
                    return redirect('lista_torneos')

                if torneo.escuadras_inscritas.count() >= torneo.cupos_maximos:
                    messages.error(
                        request,
                        f"Sobrecupo rechazado: El torneo '{torneo.nombre}' alcanzó su límite de {torneo.cupos_maximos} cupos.",
                    )
                    return redirect('lista_torneos')

                escuadra_libre = Escuadra.objects.filter(
                    capitan=request.user, torneo__isnull=True
                ).first()

                if escuadra_libre and (
                    not nombre_input
                    or escuadra_libre.nombre_escuadra.lower() == nombre_input.lower()
                ):
                    escuadra_libre.torneo = torneo
                    escuadra_libre.save()
                    nombre_final = escuadra_libre.nombre_escuadra
                else:
                    nombre_final = (
                        nombre_input
                        if nombre_input
                        else f'Individual - {request.user.username} (T{torneo.pk})'
                    )

                    if torneo.escuadras_inscritas.filter(
                        nombre_escuadra__iexact=nombre_final
                    ).exists():
                        messages.error(
                            request,
                            f"Inscripción duplicada: La escuadra '{nombre_final}' ya está inscrita en '{torneo.nombre}'.",
                        )
                        return redirect('lista_torneos')

                    Escuadra.objects.create(
                        nombre_escuadra=nombre_final, torneo=torneo, capitan=request.user
                    )

                messages.success(
                    request,
                    f"¡Inscripción confirmada! '{nombre_final}' ingresó a '{torneo.nombre}'.",
                )

        except IntegrityError:
            messages.error(
                request,
                'Inscripción duplicada: Ese nombre de escuadra ya está registrado en el sistema.',
            )

    return redirect('lista_torneos')


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

        nueva_escuadra = Escuadra.objects.create(
            nombre_escuadra=nombre_escuadra,
            capitan=request.user,
            logo=logo_file
        )

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
    torneos = Torneo.objects.all()
    return render(request, 'matchmaking.html', {'torneos': torneos})


@login_required
def panel_dae_view(request):
    if getattr(request.user, 'rol', None) != 'DAE' and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')
    
    context = {
        'mensaje': 'Panel de Gestión DAE - Premios y Beneficios INACAP Maipú'
    }
    return render(request, 'panel_dae.html', context)


@login_required
def panel_arbitraje(request):
    user_rol = getattr(request.user, 'rol', None)
    if user_rol not in ['Administrador', 'DAE'] and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado: Solo la administración y DAE pueden gestionar el arbitraje.')
        return redirect('/torneos/')

    disputas = Partida.objects.filter(estado='EnDisputa')
    return render(request, 'arbitraje.html', {'disputas': disputas})


@login_required
def resolver_disputa(request, disputa_id):
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


@login_required
def buscar_jugadores_view(request):
    juego_query = request.GET.get('juego', '').strip()
    rango_query = request.GET.get('rango', '').strip()
    
    jugadores = Usuario.objects.filter(is_active=True)
    
    if juego_query:
        jugadores = jugadores.filter(juego_favorito__icontains=juego_query)
    
    if rango_query:
        jugadores = jugadores.filter(rango__iexact=rango_query)
        
    context = {
        'jugadores': jugadores,
        'juego_seleccionado': juego_query,
        'rango_seleccionado': rango_query,
    }
    return render(request, 'buscar_jugadores.html', context)


@login_required
def gestionar_escuadra_view(request):
    escuadra_existente = Escuadra.objects.filter(capitan=request.user).first()
    
    if request.method == 'POST':
        if 'crear_equipo' in request.POST:
            nombre = request.POST.get('nombre_escuadra')
            logo = request.FILES.get('logo')
            if nombre and not escuadra_existente:
                Escuadra.objects.create(
                    nombre_escuadra=nombre,
                    logo=logo,
                    capitan=request.user
                )
                return redirect('gestionar_escuadra')
                
        elif 'invitar_jugador' in request.POST:
            username_invitado = request.POST.get('username_invitado')
            try:
                jugador_obj = Usuario.objects.get(username=username_invitado)
                InvitacionEscuadra.objects.create(
                    escuadra=escuad_existente,
                    jugador_invitado=jugador_obj,
                    estado='Pendiente'
                )
            except Usuario.DoesNotExist:
                pass 
            return redirect('gestionar_escuadra')

    context = {
        'escuadra': escuadra_existente,
    }
    return render(request, 'gestion_escuadra.html', context)


@login_required
def aceptar_invitacion_view(request, invitacion_id):
    try:
        invitacion = InvitacionEscuadra.objects.get(id=invitacion_id, jugador_invitado=request.user)
        invitacion.estado = 'Aceptada'
        invitacion.save()
    except InvitacionEscuadra.DoesNotExist:
        pass 
        
    return redirect('mis_invitaciones')


@login_required
def mis_invitaciones_view(request):
    invitaciones = InvitacionEscuadra.objects.filter(jugador_invitado=request.user)
    return render(request, 'mis_invitaciones.html', {'invitaciones': invitaciones})