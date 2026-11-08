import os
import sys

from django.core.wsgi import get_wsgi_application

# Obtiene la ruta base del proyecto para que Python encuentre tus apps (cuentas, analitica, etc.)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_final.settings')

application = get_wsgi_application()