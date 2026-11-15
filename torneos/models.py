from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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
    estado = models.CharField(max_length=20, default='Activo')
    validado_dae = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)

    # Campos para soporte de laboratorios y reservas presenciales (RF-16)
    laboratorio = models.CharField(max_length=50, blank=True, null=True)        # Ej: "L-3"
    fecha_reserva = models.DateField(blank=True, null=True)                    # Fecha de la final presencial
    horario_reserva = models.CharField(max_length=50, blank=True, null=True)   # Bloque horario

    def __str__(self):
        return f"{self.nombre} [{self.nivel_requerido}] ({self.juego})"

    def clean(self):
        super().clean()
        # Validar que los cupos sean estrictamente potencia de 2
        n = self.cupos_maximos
        if not (n > 0 and (n & (n - 1)) == 0):
            raise ValidationError({'cupos_maximos': 'Los cupos máximos del torneo deben ser obligatoriamente una potencia de 2 (4, 8, 16, 32, 64).'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Fuerza la ejecución de clean() antes de guardar
        super().save(*args, **kwargs)

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
    logo = models.ImageField(upload_to='logos_escuadras/', blank=True, null=True) # Soporte para imagen/logo
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='escuadras_inscritas', null=True, blank=True)
    capitan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escuadras_lideradas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_escuadra


class InvitacionEscuadra(models.Model):
    """
    Gestiona las invitaciones de jugadores a una escuadra (CP-HU03-04).
    """
    escuadra = models.ForeignKey(Escuadra, on_delete=models.CASCADE, related_name='invitaciones')
    jugador_invitado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_recibidas')
    estado = models.CharField(max_length=20, default='Pendiente', choices=[
        ('Pendiente', 'Pendiente'),
        ('Aceptada', 'Aceptada'),
        ('Rechazada', 'Rechazada')
    ])
    fecha_invitacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('escuadra', 'jugador_invitado')

    def __str__(self):
        return f"Invitación de {self.escuadra.nombre_escuadra} a {self.jugador_invitado.username} [{self.estado}]"


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


class MensajeChat(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='mensajes')
    emisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.emisor.username}"


class EvidenciaPartida(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='evidencias')
    capitan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    marcador = models.CharField(max_length=20)
    archivo = models.FileField(upload_to='evidencias_partidas/')
    estado = models.CharField(max_length=20, default='Pendiente')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.capitan.username} - {self.marcador}"