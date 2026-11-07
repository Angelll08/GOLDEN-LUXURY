from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class CorreoOUsuarioBackend(ModelBackend):
    """Permite iniciar sesión escribiendo el nombre de usuario O el correo."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        Usuario = get_user_model()
        if username is None:
            username = kwargs.get(Usuario.USERNAME_FIELD)
        if not username or password is None:
            return None
        for usuario in Usuario.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)):
            if usuario.check_password(password) and self.user_can_authenticate(usuario):
                return usuario
        return None
