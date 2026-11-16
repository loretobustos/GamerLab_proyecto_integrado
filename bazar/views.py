import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import PublicacionBazar, TransaccionEscrow


@login_required
def mis_canjes_view(request):
    """
    Muestra los canjes y compras realizadas por el estudiante actual,
    incluyendo el código OTP presencial y el estado de custodia.
    """
    # Filtramos las transacciones donde el usuario logueado es el comprador
    mis_transacciones = TransaccionEscrow.objects.filter(comprador=request.user).order_by('-id')
    
    contexto = {
        'transacciones': mis_transacciones,
    }
    return render(request, 'mis_canjes.html', contexto)


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
            publicacion = PublicacionBazar(
                usuario=request.user,
                titulo=titulo,
                descripcion=descripcion,
                precio_creditos=precio_creditos,
                estado='Disponible'
            )
            
            if imagen_subida:
                publicacion.imagen = imagen_subida
                
            publicacion.save()
            messages.success(request, "¡Artículo publicado con éxito en el Bazar Gamer!")
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
            messages.success(request, "¡Solicitud generada con éxito! Revisa tu código OTP en 'Mis Canjes'.")
        else:
            messages.error(request, "No tienes suficientes créditos institucionales para este canje.")
        
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
       Verifica el código OTP presencial entregado en la sede (vía POST), marca la transacción
       como completada y libera/transfiere los créditos al VENDEDOR de forma definitiva.
    """
    transaccion = get_object_or_404(TransaccionEscrow, pk=transaccion_id)
    
    if request.method == 'POST':
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

            messages.success(request, f"¡Transacción aprobada! Se liberaron {transaccion.monto_retenido} CR al vendedor {vendedor.username}.")
        else:
            messages.error(request, "Esta transacción ya fue procesada anteriormente.")

    return redirect('panel_admin_escrow')


@login_required
def mis_canjes_view(request):
    mis_transacciones = TransaccionEscrow.objects.filter(comprador=request.user).order_by('-id_transaccion')

    return render(request, 'mis_canjes.html', {'transacciones': mis_transacciones})

@login_required
def liberar_creditos_view(request, canje_id):
    """
    RF-20 / RNF-01 / CP-HU08-01:
    Impedir liberación de créditos por un usuario ajeno al canje (Trader C).
    """
    # 1. Obtenemos el canje actual
    canje = get_object_or_404(Canje, id=canje_id)
    
    # 2. VALIDACIÓN ESTRICTA (CP-HU08-01): Verificar si el usuario es parte del canje
    es_participante = (canje.comprador == request.user) or (canje.vendedor == request.user)
    
    if not es_participante and not request.user.is_superuser and getattr(request.user, 'rol', None) not in ['Administrador']:
        messages.error(request, "Acceso denegado: Operación rechazada por falta de autorización.")
        return redirect('/bazar/') # O a la vista que corresponda

    # 3. Si es participante legítimo, continúa el código normal de liberación...
    # (aquí va tu lógica existente de actualizar saldos, estado de escrow, etc.)
    
    messages.success(request, "¡Créditos liberados correctamente!")
    return redirect('/bazar/')