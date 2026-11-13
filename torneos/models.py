from django.db import models
from django.conf import settings

class Torneo(models.Model):
    id_torneo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    juego = models.CharField(max_length=50) # Valorant, LoL, EA FC 26
    cupos_maximos = models.IntegerField(default=16) # Potencia de 2: 8, 16, 32
    premio_creditos = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    estado = models.CharField(max_length=30, default='Abierto', choices=[
        ('Abierto', 'Abierto'),
        ('EnCurso', 'En Curso'),
        ('Finalizado', 'Finalizado')
    ])
    fecha_inicio = models.DateTimeField()

    def __str__(self):
        return f"{self.nombre} ({self.juego})"


class Escuadra(models.Model):
    id_escuadra = models.AutoField(primary_key=True)
    nombre_escuadra = models.CharField(max_length=50)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='escuadras')
    capitan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='escuadras_lideradas')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_escuadra} - {self.torneo.nombre}"


class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='partidas')
    equipo_local = models.ForeignKey(Escuadra, on_delete=models.CASCADE, related_name='partidas_local')
    equipo_visita = models.ForeignKey(Escuadra, on_delete=models.CASCADE, related_name='partidas_visita')
    resultado_local = models.IntegerField(default=0)
    resultado_visita = models.IntegerField(default=0)
    estado = models.CharField(max_length=30, default='Programada', choices=[
        ('Programada', 'Programada'),
        ('EnJuego', 'En Juego'),
        ('EnDisputa', 'En Disputa'),
        ('Finalizada', 'Finalizada')
    ])

    def __str__(self):
        return f"Partida #{self.id_partida}: {self.equipo_local} vs {self.equipo_visita}"