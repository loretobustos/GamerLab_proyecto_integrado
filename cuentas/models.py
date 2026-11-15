from django.contrib.auth.models import AbstractUser
from django.db import models

class Carrera(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    ROLES = (
        ('Jugador', 'Jugador / Estudiante'),
        ('Administrador', 'Administrador de Sede'),
        ('DAE', 'DAE / Curricular (Gestión de Premios)'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='Jugador')
    run = models.CharField(max_length=12, unique=True, null=True, blank=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True)
    saldo_creditos = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)

    # --- NUEVOS CAMPOS PARA PERFIL GAMER (RF-10) ---
    gamertag = models.CharField(max_length=50, blank=True, null=True)
    juego_favorito = models.CharField(max_length=100, blank=True, null=True)
    rango = models.CharField(max_length=50, blank=True, null=True)

    # Evitar conflictos con los related_name por defecto de Django
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )