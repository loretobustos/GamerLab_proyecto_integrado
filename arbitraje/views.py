from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Disputa

@login_required
def sala_disputas_view(request):
    """
    Sala de revisión técnica de partidas impugnadas (HU-02).
    """
    disputas = Disputa.objects.filter(estado='EnDisputa')
    return render(request, 'arbitraje.html', {'disputas': disputas})

@login_required
def resolver_disputa_view(request, disputa_id):
    """
    Emisión de dictamen arbitral y cierre de disputa.
    """
    disputa = get_object_or_404(Disputa, pk=disputa_id)
    
    if request.method == 'POST':
        dictamen = request.POST.get('dictamen_arbitro')
        
        disputa.dictamen_arbitro = dictamen
        disputa.estado = 'Resuelta'
        disputa.save()
        
        return redirect('sala_disputas')
        
    return redirect('sala_disputas')