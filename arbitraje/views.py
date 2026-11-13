from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Disputa

def es_admin_o_arbitro(user):
    # Verifica si el usuario es staff, superusuario o tiene rol de Administrador/Árbitro
    return user.is_authenticated and (user.is_staff or getattr(user, 'rol', '') in ['Administrador', 'Árbitro'])

@login_required
@user_passes_test(es_admin_o_arbitro, login_url='home')
def sala_disputas_view(request):
    """
    Vista exclusiva para administradores/árbitros (Bloquea a jugadores estándar).
    """
    disputas = Disputa.objects.filter(estado='EnDisputa')
    return render(request, 'arbitraje.html', {'disputas': disputas})

@login_required
@user_passes_test(es_admin_o_arbitro, login_url='home')
def resolver_disputa_view(request, disputa_id):
    disputa = get_object_or_404(Disputa, pk=disputa_id)
    if request.method == 'POST':
        dictamen = request.POST.get('dictamen_arbitro')
        disputa.dictamen_arbitro = dictamen
        disputa.estado = 'Resuelta'
        disputa.save()
        return redirect('sala_disputas')
    return redirect('sala_disputas')