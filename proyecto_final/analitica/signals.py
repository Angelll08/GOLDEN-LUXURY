from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Acceso
from .utils import obtener_ip


@receiver(user_logged_in)
def registrar_acceso(sender, request, user, **kwargs):
    try:
        Acceso.objects.create(
            usuario=user,
            ip=obtener_ip(request),
            navegador=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
    except Exception:
        pass  # si falla el registro, no se rompe el inicio de sesión
