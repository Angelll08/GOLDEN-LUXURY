from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import Resolver404, resolve

# Páginas que un visitante SIN sesión sí puede abrir
PUBLICAS = {'inicio', 'login', 'registro', 'evento'}
PREFIJOS_LIBRES = ('/admin/', '/accounts/')


class SesionObligatoriaMiddleware:
    """Un visitante puede ver el inicio, pero para navegar debe iniciar sesión o crear cuenta."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and self._requiere_sesion(request.path_info):
            messages.info(request, 'Inicia sesión o crea tu cuenta para poder navegar en el sitio.')
            return redirect_to_login(request.get_full_path())
        return self.get_response(request)

    @staticmethod
    def _requiere_sesion(ruta):
        libres = PREFIJOS_LIBRES + (settings.STATIC_URL, settings.MEDIA_URL)
        if ruta.startswith(libres):
            return False
        try:
            nombre = resolve(ruta).url_name
        except Resolver404:
            return False   # que Django muestre su 404
        return nombre not in PUBLICAS
