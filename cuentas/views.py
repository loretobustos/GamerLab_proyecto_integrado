from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import PerfilGamer, Usuario, Carrera

def registro_view(request):
    carreras = Carrera.objects.all()
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        gamertag = request.POST.get('gamertag')
        run = request.POST.get('run_identificador')
        carrera_id = request.POST.get('id_carrera')

        if not email.endswith('@inacapmail.cl'):
            error = "Debes utilizar tu correo institucional de INACAP (@inacapmail.cl)."
            return render(request, 'registro.html', {'carreras': carreras, 'error': error})

        if Usuario.objects.filter(username=username).exists():
            error = "El nombre de usuario ya está en uso."
            return render(request, 'registro.html', {'carreras': carreras, 'error': error})

        carrera_obj = Carrera.objects.filter(pk=carrera_id).first()

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            rol='Jugador',
            run_identificador=run,
            id_carrera=carrera_obj,
            saldo_creditos=50.00,
            reputacion=5.00
        )
        PerfilGamer.objects.create(usuario=user, apodo_gamertag=gamertag)

        login(request, user)
        return redirect('home')

    return render(request, 'registro.html', {'carreras': carreras, 'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        username_ingresado = request.POST.get('username')
        password_ingresado = request.POST.get('password')

        user = authenticate(request, username=username_ingresado, password=password_ingresado)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Credenciales inválidas. Verifica tu usuario y contraseña."

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')