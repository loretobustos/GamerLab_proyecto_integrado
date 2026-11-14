from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    juego = models.CharField(max_length=50)
    cupos_maximos = models.IntegerField(default=16) # Ej: 8, 16, 32
    premio_creditos = models.IntegerField(default=500)
    estado = models.CharField(max_length=20, default='Activo')

    def clean(self):
        super().clean()
        # Validar que los cupos sean potencia de 2
        n = self.cupos_maximos
        if not (n > 0 and (n & (n - 1)) == 0):
            raise ValidationError({'cupos_maximos': 'Los cupos máximos del torneo deben ser obligatoriamente una potencia de 2 (8, 16, 32, 64).'})

    def save(self, *args, **kwargs):
        self.full_clean() # Fuerza la ejecución de clean() antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.juego})"
class Torneo(models.Model):
    id_torneo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    juego = models.CharField(max_length=100, default="General")
    nivel_requerido = models.CharField(max_length=30, default='Abierto', choices=[
        ('Abierto', 'Abierto (Todos los niveles)'),
        ('Inicial', 'Inicial / Novato'),
        ('Intermedio', 'Intermedio'),
        ('Experto', 'Experto / Competitivo')
    ])
    cupos_maximos = models.IntegerField(default=16)
    premio_creditos = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    fecha_inicio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} [{self.nivel_requerido}]"

    def promedio_estrellas(self):
        calificaciones = self.calificaciones.all()
        if not calificaciones:
            return 0
        return round(sum(c.puntuacion for c in calificaciones) / calificaciones.count(), 1)


class Escuadra(models.Model):
    """
    Modelo para los equipos o escuadras que participan en los torneos.
    """
    id_escuadra = models.AutoField(primary_key=True)
    nombre_escuadra = models.CharField(max_length=100, unique=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='escuadras_inscritas', null=True, blank=True)
    capitan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escuadras_lideradas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_escuadra


class Partida(models.Model):
    """
    Encuentros o partidas programadas dentro de los torneos.
    """
    id_partida = models.AutoField(primary_key=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='partidas', null=True, blank=True)
    equipo_local = models.ForeignKey(Escuadra, on_delete=models.CASCADE, related_name='partidas_local', null=True, blank=True)
    equipo_visita = models.ForeignKey(Escuadra, on_delete=models.CASCADE, related_name='partidas_visita', null=True, blank=True)
    resultado_local = models.IntegerField(default=0)
    resultado_visita = models.IntegerField(default=0)
    estado = models.CharField(max_length=30, default='Programada', choices=[
        ('Programada', 'Programada'),
        ('EnJuego', 'En Juego'),
        ('Finalizada', 'Finalizada'),
        ('EnDisputa', 'En Disputa')
    ])

    def __str__(self):
        local = self.equipo_local.nombre_escuadra if self.equipo_local else "TBD"
        visita = self.equipo_visita.nombre_escuadra if self.equipo_visita else "TBD"
        return f"{local} vs {visita}"


class CalificacionTorneo(models.Model):
    """
    Evaluación de 1 a 5 estrellas del torneo por parte de los participantes.
    """
    id_calificacion = models.AutoField(primary_key=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(default=5)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('torneo', 'usuario')

    def __str__(self):
        return f"{self.torneo.nombre} - {self.puntuacion} ⭐"