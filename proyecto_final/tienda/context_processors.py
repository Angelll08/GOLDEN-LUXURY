from .carrito import Carrito
from .models import Pedido


def carrito(request):
    """Datos disponibles en todas las plantillas: piezas del carrito y pedido entregado sin calificar."""
    contexto = {'carrito_cantidad': len(Carrito(request)), 'encuesta_pendiente': None}
    usuario = getattr(request, 'user', None)
    if usuario is not None and usuario.is_authenticated:
        contexto['encuesta_pendiente'] = (
            Pedido.objects.filter(usuario=usuario, estado='entregado', encuesta__isnull=True)
            .order_by('-creado').first()
        )
    return contexto
