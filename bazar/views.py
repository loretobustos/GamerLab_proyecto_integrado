import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PublicacionBazar, TransaccionEscrow

def bazar_catalogo_view(request):
    query = request.GET.get('q', '')
    if query:
        articulos = PublicacionBazar.objects.filter(titulo__icontains=query, estado='Disponible')
    else:
        articulos = PublicacionBazar.objects.filter(estado='Disponible')
        
    return render(request, 'bazar.html', {'articulos': articulos, 'query': query})

@login_required
def solicitar_canje_view(request, publicacion_id):
    articulo = get_object_or_404(PublicacionBazar, pk=publicacion_id)
    
    if request.method == 'POST':
        # Validar que el comprador tenga suficientes créditos
        if request.user.saldo_creditos >= articulo.precio_creditos:
            # Retener créditos en Escrow
            request.user.saldo_creditos -= articulo.precio_creditos
            request.user.save()

            articulo.estado = 'Reservado'
            articulo.save()

            # Generar código OTP aleatorio de 6 dígitos para la entrega presencial
            otp_code = str(random.randint(100000, 999999))

            TransaccionEscrow.objects.create(
                publicacion=articulo,
                comprador=request.user,
                monto_retenido=articulo.precio_creditos,
                codigo_otp_presencial=otp_code,
                estado_escrow='RetenidoEnCustodia'
            )
        
        return redirect('bazar_catalogo')
    return redirect('bazar_catalogo')