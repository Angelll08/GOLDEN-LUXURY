from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from tienda.models import Categoria


class Command(BaseCommand):
    help = 'Carga categorías, productos y tallas de demostración (fixture datos_demo) solo si la tienda está vacía.'

    def handle(self, *args, **opciones):
        if Categoria.objects.exists():
            self.stdout.write('La tienda ya tiene datos: no se carga la demostración.')
            return
        try:
            call_command('loaddata', 'datos_demo')
        except CommandError:
            self.stdout.write('No se encontró el archivo tienda/fixtures/datos_demo.json: se omite.')
            return
        self.stdout.write(self.style.SUCCESS('Datos de demostración cargados.'))
