import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Usuario, Carrera
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.contrib import messages

class GamerLabPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class GamerLabPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class GamerLabPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class GamerLabPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


def validar_run_chileno(run_str):
    if not run_str:
        return False

    run_limpio = str(run_str).replace('.', '').replace(' ', '').strip().upper()
    cuerpo, guion, dv = run_limpio.partition('-')

    if not guion or not cuerpo.isdigit() or len(cuerpo) < 7 or len(cuerpo) > 8:
        return False

    suma = 0
    multiplo = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    resto = suma % 11
    dv_calc = 11 - resto

    if dv_calc == 11:
        dv_esperado = '0'
    elif dv_calc == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_calc)

    return dv == dv_esperado


def registro_view(request):
    error = None
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''

        run = (request.POST.get('run_identificador') or '').replace('.', '').replace(' ', '').strip().upper()

        carrera_id = request.POST.get('id_carrera')
        rol_seleccionado = request.POST.get('rol', 'Jugador')

        if not email.endswith('@inacapmail.cl'):
            error = "El correo debe pertenecer al dominio institucional (@inacapmail.cl)."

        elif not validar_run_chileno(run):
            error = "El RUN ingresado no es válido (revisa el dígito verificador)."

        elif Usuario.objects.filter(username=username).exists():
            error = "El nombre de usuario ya está en uso."
        elif Usuario.objects.filter(email=email).exists():
            error = "El correo electrónico ya está registrado."
        elif Usuario.objects.filter(run=run).exists():
            error = "El RUN ya se encuentra registrado en el sistema."
        else:
            try:
                carrera_obj = Carrera.objects.filter(id=carrera_id).first() if carrera_id else None

                roles_validos = ['Jugador', 'Administrador', 'DAE']
                if rol_seleccionado not in roles_validos:
                    rol_seleccionado = 'Jugador'

                nuevo_usuario = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    run=run,
                    carrera=carrera_obj,
                    rol=rol_seleccionado,
                )

                if rol_seleccionado in ['Administrador', 'DAE']:
                    nuevo_usuario.is_staff = True
                    nuevo_usuario.save()

                return redirect('login')
            except Exception as e:
                error = f"Error al guardar en base de datos: {str(e)}"

    carreras = Carrera.objects.all()
    return render(request, 'registro.html', {'carreras': carreras, 'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        identificador = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        # Si el usuario escribió un correo, buscamos su username real primero
        username_real = identificador
        if '@' in identificador:
            usuario_obj = Usuario.objects.filter(email__iexact=identificador).first()
            if usuario_obj:
                username_real = usuario_obj.username
        else:
            # Permite iniciar sesión aunque escriba mayúsculas distintas en su usuario
            usuario_obj = Usuario.objects.filter(username__iexact=identificador).first()
            if usuario_obj:
                username_real = usuario_obj.username

        user = authenticate(request, username=username_real, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Usuario o contraseña incorrectos."

    return render(request, 'login.html', {'error': error})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def perfil_view(request):
    return render(request, 'perfil.html')


@login_required
def perfil_billetera_view(request):
    contexto = {
        'usuario': request.user,
    }
    return render(request, 'perfil.html', contexto)


@login_required
def panel_dae_view(request):
    # Validación estricta para asegurar que solo roles institucionales DAE o Admin accedan
    if request.user.rol not in ['DAE', 'Administrador'] and not request.user.is_superuser:
        return HttpResponseForbidden("Acceso denegado: No tienes permisos institucionales DAE.")
    return render(request, 'panel_dae.html')


@login_required
def editar_perfil_view(request):
    """
    Permite registrar y actualizar los datos del perfil gamer (Gamertag, Juego, Rango)
    con validaciones de seguridad contra duplicados y caracteres no permitidos (CP-HU03-02).
    """
    if request.method == 'POST':
        gamertag = request.POST.get('gamertag', '').strip()
        juego_favorito = request.POST.get('juego_favorito', '').strip()
        rango = request.POST.get('rango', '').strip()

        # 1. Validación de contenido no permitido / caracteres maliciosos (Ej: etiquetas HTML o inyecciones)
        if gamertag and not re.match(r"^[\w\s\-#]+$", gamertag):
            messages.error(request, "Error: El gamertag contiene caracteres no permitidos o contenido potencialmente malicioso.")
            return redirect('perfil')

        # 2. Validación de Gamertag Duplicado (excluyendo al propio usuario actual)
        if gamertag and Usuario.objects.filter(gamertag__iexact=gamertag).exclude(id=request.user.id).exists():
            messages.error(request, "Error: El gamertag ingresado ya se encuentra registrado por otro jugador.")
            return redirect('perfil')

        # Guardado seguro
        request.user.gamertag = gamertag
        request.user.juego_favorito = juego_favorito
        request.user.rango = rango
        request.user.save()
        
        messages.success(request, "¡Perfil gamer actualizado correctamente!")
        return redirect('perfil')

    return render(request, 'perfil.html')

@login_required
def buscar_jugadores_view(request):
    """
    Permite filtrar a los jugadores registrados por videojuego favorito y rango (CP-HU03-03).
    """
    juego = request.GET.get('juego', '').strip()
    rango = request.GET.get('rango', '').strip()

    # Partimos filtrando solo a los usuarios que tengan rol de Jugador
    jugadores = Usuario.objects.filter(rol='Jugador')

    if juego:
        jugadores = jugadores.filter(juego_favorito__icontains=juego)
    
    if rango:
        jugadores = jugadores.filter(rango__iexact=rango)

    contexto = {
        'jugadores': jugadores,
        'juego_seleccionado': juego,
        'rango_seleccionado': rango,
    }
    return render(request, 'buscar_jugadores.html', contexto)