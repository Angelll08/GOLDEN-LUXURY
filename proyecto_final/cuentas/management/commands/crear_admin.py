import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea el administrador con ADMIN_USER, ADMIN_EMAIL y ADMIN_PASSWORD (si no existe). Útil en Render, que no da terminal gratis.'

    def handle(self, *args, **opciones):
        usuario = os.environ.get('ADMIN_USER')
        correo = os.environ.get('ADMIN_EMAIL', '')
        clave = os.environ.get('ADMIN_PASSWORD')
        if not usuario or not clave:
            self.stdout.write('Sin ADMIN_USER o ADMIN_PASSWORD: no se crea administrador.')
            return
        Usuario = get_user_model()
        if Usuario.objects.filter(username=usuario).exists():
            self.stdout.write('El administrador ya existe.')
            return
        Usuario.objects.create_superuser(username=usuario, email=correo, password=clave)
        self.stdout.write(self.style.SUCCESS('Administrador creado.'))
