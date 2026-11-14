from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from torneos.views import lista_torneos_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    # AQUÍ ESTÁ LA CLAVE: Agregamos name='home'
    path('', include('torneos.urls')),       
    path('cuentas/', include('cuentas.urls')),
    path('bazar/', include('bazar.urls')),
    path('arbitraje/', include('arbitraje.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)