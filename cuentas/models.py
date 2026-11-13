from django.contrib.auth.models import AbstractUser
from django.db import models

class Carrera(models.Model):
    id_carrera = models.CharField(max_length=50, primary_key=True)
    nombre_carrera = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_carrera


class Usuario(AbstractUser):
    """
    Modelo de Usuario extendido para la plataforma GamerLab, 
    incorporando roles institucionales (RBAC) y saldo de créditos[cite: 16, 20].
    """
    id_carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True)
    rol = models.CharField(max_length=50, choices=[
        ('Admin', 'Administrador de Plataforma y Torneos'),
        ('Jugador', 'Jugador / Capitán de Escuadra'),
        ('Gestor_DAE', 'Gestor DAE / Docente'),
        ('Trader', 'Trader Gamer')
    ], default='Jugador')
    run_identificador = models.CharField(max_length=12, unique=True, null=True, blank=True, help_text="RUT o identificador nacional")
    estado_cuenta = models.BooleanField(default=True, help_text="Bandera de actividad o suspensión disciplinaria")
    reputacion = models.FloatField(default=5.0, help_text="Calificación comunitaria en el bazar")
    saldo_creditos = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, help_text="Balance de créditos institucionales")
    
    # Campos para Autenticación de Doble Factor (2FA / TOTP)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.rol})"


class PerfilGamer(models.Model):
    """
    Identidad competitiva y nivel ELO de los estudiantes en los torneos[cite: 16].
    """
    id_perfil = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_gamer')
    apodo_gamertag = models.CharField(max_length=100, unique=True, help_text="Pseudónimo en sala de juego")
    rango = models.CharField(max_length=50, default='Bronce')
    nivel_elo = models.IntegerField(default=1000, help_text="Puntuación numérica para matchmaking")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.apodo_gamertag