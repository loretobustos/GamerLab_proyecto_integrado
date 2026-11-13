import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import PublicacionBazar, TransaccionEscrow

def bazar_catalogo_view(request):
    """
    Muestra el catálogo general de artículos disponibles en el bazar.
    """
    query = request.GET.get('q', '')
    if query:
        articulos = PublicacionBazar.objects.filter(titulo__icontains=query, estado='Disponible')
    else:
        articulos = PublicacionBazar.objects.filter(estado='Disponible')
        
    return render(request, 'bazar.html', {'articulos': articulos, 'query': query})

@login_required
def crear_publicacion_bazar_view(request):
    """
    Permite a cualquier estudiante publicar un producto (teclado, mouse, etc.)
    en el bazar fijando su precio en créditos, con o sin imagen.
    """
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        precio_creditos = request.POST.get('precio_creditos')
        
        # Capturamos la imagen solo si el usuario la seleccionó
        imagen_subida = request.FILES.get('imagen', None)

        if titulo and precio_creditos:
            # Creamos la publicación manejando el campo de imagen de forma segura
            publicacion = PublicacionBazar(
                usuario=request.user,
                titulo=titulo,
                descripcion=descripcion,
                precio_creditos=precio_creditos,
                estado='Disponible'
            )
            
            # Solo asignamos la imagen si viene en la petición
            if imagen_subida:
                publicacion.imagen = imagen_subida
                
            publicacion.save()
            return redirect('bazar_catalogo')

    return render(request, 'crear_publicacion.html')

@login_required
def solicitar_canje_view(request, publicacion_id):
    """
    1. EL JUGADOR SOLICITA EL CANJE: 
       Se le descuentan los créditos de su saldo preventivamente y se retienen en custodia (Escrow).
       El artículo pasa a estado 'Reservado' y se genera un código OTP presencial.
    """
    articulo = get_object_or_404(PublicacionBazar, pk=publicacion_id)
    
    if request.method == 'POST':
        if request.user.saldo_creditos >= articulo.precio_creditos:
            # Descontar al comprador preventivamente
            request.user.saldo_creditos -= articulo.precio_creditos
            request.user.save()

            articulo.estado = 'Reservado'
            articulo.save()

            # Generar el código OTP presencial para validar en la sede
            otp_code = str(random.randint(100000, 999999))

            TransaccionEscrow.objects.create(
                publicacion=articulo,
                comprador=request.user,
                monto_retenido=articulo.precio_creditos,
                codigo_otp_presencial=otp_code,
                estado_escrow='RetenidoEnCustodia'  # Quedan congelados esperando al admin
            )
        
        return redirect('bazar_catalogo')
    return redirect('bazar_catalogo')


def es_admin(user):
    """
    Verifica si el usuario es Administrador o staff.
    """
    return user.is_authenticated and (user.is_staff or getattr(user, 'rol', '') == 'Administrador')


@login_required
@user_passes_test(es_admin, login_url='bazar_catalogo')
def panel_admin_escrow_view(request):
    """
    PANEL EXCLUSIVO DEL ADMIN: Muestra todas las transacciones en custodia
    pendientes de validación presencial mediante código OTP.
    """
    transacciones = TransaccionEscrow.objects.filter(estado_escrow='RetenidoEnCustodia')
    return render(request, 'admin_bazar.html', {'transacciones': transacciones})


@login_required
@user_passes_test(es_admin, login_url='bazar_catalogo')
def aprobar_canje_admin_view(request, transaccion_id):
    """
    2. EL ADMINISTRADOR APRUEBA: 
       Verifica el código OTP presencial entregado en la sede, marca la transacción
       como completada y libera/transfiere los créditos al VENDEDOR de forma definitiva.
    """
    transaccion = get_object_or_404(TransaccionEscrow, pk=transaccion_id)
    
    if transaccion.estado_escrow == 'RetenidoEnCustodia':
        # Marcar transacción como completada
        transaccion.estado_escrow = 'Completado'
        transaccion.save()

        # Marcar artículo como canjeado
        articulo = transaccion.publicacion
        articulo.estado = 'Canjeado'
        articulo.save()

        # Transferir los créditos retenidos al usuario que publicó (Vendedor)
        vendedor = articulo.usuario
        vendedor.saldo_creditos += transaccion.monto_retenido
        vendedor.save()

    return redirect('panel_admin_escrow')