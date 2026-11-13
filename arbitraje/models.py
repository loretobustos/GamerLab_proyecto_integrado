from django.db import models
from torneos.models import Partida
from django.conf import settings
from django.utils import timezone

class Disputa(models.Model):
    id_disputa = models.AutoField(primary_key=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='disputas')
    usuario_reporta = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportes_disputa', null=True, blank=True)
    motivo = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=30, default='EnDisputa', choices=[
        ('EnDisputa', 'En Disputa'),
        ('Resuelta', 'Resuelta')
    ])
    dictamen_arbitro = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Disputa #{self.id_disputa} - Partida #{self.partida.id_partida}"