from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Usuario, Carrera

def validar_run_chileno(run_str):
    """
    Valida el RUN chileno usando el algoritmo del Módulo 11.
    Ejemplo de formato esperado: '12345678-9' o '12345678-K'
    """
    try:
        run_str = run_str.replace('.', '').upper()
        if '-' not in run_str:
            return False
        
        cuerpo, dv = run_str.split('-')
        if not cuerpo.isdigit():
            return False

        suma = 0
        multiplo = 2

        # Recorrer el cuerpo de derecha a izquierda
        for r in reversed(cuerpo):
            suma += int(r) * multiplo
            multiplo += 1
            if multiplo > 7:
                multiplo = 2

        resto = suma % 11
        resultado = 11 - resto

        if resultado == 11:
            dv_esperado = '0'
        elif resultado == 10:
            dv_esperado = 'K'
        else:
            dv_esperado = str(resultado)

        return dv_esperado == dv
    except Exception:
        return False


def registro_view(request):
    error = None
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        # Los nombres coinciden con los "name" del formulario registro.html
        run = (request.POST.get('run_identificador') or '').replace('.', '').strip().upper()
        carrera_id = request.POST.get('id_carrera')

        # 1. Validación estricta del correo institucional
        if not email.endswith('@inacapmail.cl'):
            error = "El correo debe pertenecer al dominio institucional (@inacapmail.cl)."

        # 2. Validación estricta del RUN chileno (Módulo 11)
        elif not validar_run_chileno(run):
            error = "El RUN ingresado no es válido (revisa el dígito verificador)."

        # 3. Validar si ya existe el usuario, correo o RUN
        elif Usuario.objects.filter(username=username).exists():
            error = "El nombre de usuario ya está en uso."
        elif Usuario.objects.filter(email=email).exists():
            error = "El correo electrónico ya está registrado."
        elif Usuario.objects.filter(run=run).exists():
            error = "El RUN ya se encuentra registrado en el sistema."
        else:
            carrera_obj = Carrera.objects.filter(id=carrera_id).first()

            # Seguridad: todo registro público nace como Jugador.
            # El rol Administrador solo se asigna desde el panel de administración.
            Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                run=run,
                carrera=carrera_obj,
                rol='Jugador',
            )
            return redirect('login')

    carreras = Carrera.objects.all()
    return render(request, 'registro.html', {'carreras': carreras, 'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
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
    """
    Muestra los datos del perfil del estudiante y su saldo actual de créditos.
    """
    return render(request, 'perfil.html')
@login_required
def editar_perfil_view(request):
    """
    Vista temporal para edición de perfil del usuario.
    """
    return render(request, 'perfil.html')