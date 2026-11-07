import hashlib
from decimal import Decimal

from .models import Variante


class Carrito:
    """Carrito en la sesión. Cada línea: {'v': variante_id, 'c': cantidad, 'd': dorsal, 'n': nombre}.
    Una misma talla con distinto dorsal/nombre cuenta como líneas separadas."""

    def __init__(self, request):
        self.session = request.session
        items = self.session.get('carrito')
        if not isinstance(items, dict) or any(not isinstance(v, dict) for v in items.values()):
            items = {}          # formato viejo o vacío
        self.items = items

    def _guardar(self):
        self.session['carrito'] = self.items
        self.session.modified = True

    @staticmethod
    def _clave(variante_id, dorsal, nombre):
        return hashlib.md5(f'{variante_id}|{dorsal}|{nombre}'.encode('utf-8')).hexdigest()[:12]

    def _otras_lineas(self, variante_id, excepto):
        return sum(l['c'] for k, l in self.items.items() if l['v'] == variante_id and k != excepto)

    def agregar(self, variante, cantidad=1, dorsal='', nombre=''):
        clave = self._clave(variante.id, dorsal, nombre)
        linea = self.items.get(clave, {'v': variante.id, 'c': 0, 'd': dorsal, 'n': nombre})
        disponible = max(variante.stock - self._otras_lineas(variante.id, clave), 0)
        linea['c'] = min(linea['c'] + cantidad, disponible)     # nunca más que el stock
        if linea['c'] > 0:
            self.items[clave] = linea
            self._guardar()
        return linea['c']

    def quitar(self, clave):
        if clave in self.items:
            del self.items[clave]
            self._guardar()

    def limpiar(self):
        self.items = {}
        self._guardar()

    def __iter__(self):
        ids = list({l['v'] for l in self.items.values()})
        variantes = Variante.objects.select_related('producto__categoria').in_bulk(ids)
        for clave, l in list(self.items.items()):
            v = variantes.get(l['v'])
            if v is None:
                continue
            cat = v.producto.categoria
            personalizado = bool(l['d'] or l['n']) and cat.permite_personalizacion
            extra = cat.costo_personalizacion if personalizado else Decimal('0')
            yield {
                'clave': clave,
                'variante': v,
                'cantidad': l['c'],
                'dorsal': l['d'] if personalizado else '',
                'nombre': l['n'] if personalizado else '',
                'personalizado': personalizado,
                'extra': extra,
                'subtotal': (v.producto.precio + extra) * l['c'],
            }

    def __len__(self):
        return sum(l['c'] for l in self.items.values())

    def total(self):
        return sum((i['subtotal'] for i in self), Decimal('0'))
