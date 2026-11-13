from django.db import models
from django.conf import settings

class PublicacionBazar(models.Model):
    id_publicacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('cuentas.Usuario', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_creditos = models.DecimalField(max_digits=10, decimal_places=2)
    # EL NOMBRE DEBE SER ESTE:
    imagen = models.ImageField(upload_to='bazar/', blank=True, null=True) 
    estado = models.CharField(max_length=30, default='Disponible')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.titulo} ({self.precio_creditos} CR)"


class TransaccionEscrow(models.Model):
    id_transaccion = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(PublicacionBazar, on_delete=models.CASCADE, related_name='transacciones')
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compras_escrow')
    monto_retenido = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_otp_presencial = models.CharField(max_length=6, blank=True, null=True)
    estado_escrow = models.CharField(max_length=30, default='RetenidoEnCustodia', choices=[
        ('RetenidoEnCustodia', 'Retenido en Custodia'),
        ('Completado', 'Completado'),
        ('Reembolsado', 'Reembolsado'),
        ('EnDisputa', 'En Disputa')
    ])
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Escrow #{self.id_transaccion} - {self.monto_retenido} CR"