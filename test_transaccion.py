import os
import django

# Configurar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamerlab_project.settings')
django.setup()

from django.db import transaction

def probar_rollback():
    print("--> Iniciando entrega masiva de premios...")
    try:
        with transaction.atomic():
            print("-> Acreditado integrante 1...")
            print("-> Acreditado integrante 2...")
            print("-> Acreditado integrante 3...")
            print("!! Corte de red detectado en el integrante 4. Lanzando excepción...")
            raise Exception("Error de red: Conexión perdida con el servidor de pagos.")
    except Exception as e:
        print(f"!! Transacción fallida capturada: {e}")
        print("--> ¡ROLLBACK EJECUTADO! Ningún saldo parcial fue guardado.")

if __name__ == '__main__':
    probar_rollback()