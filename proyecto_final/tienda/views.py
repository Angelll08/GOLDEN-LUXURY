import re
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from . import chat as sala
from . import pagos
from .carrito import Carrito
from .forms import CheckoutForm, EncuestaForm
from .models import Categoria, Encuesta, ItemPedido, Pedido, Producto, Variante


NOMBRE_BORDADO = re.compile(r"^[A-ZÁÉÍÓÚÜÑ .'-]{1,12}$")


def inicio(request):
    return render(request, 'tienda/inicio.html', {
        'destacados': Producto.objects.filter(activo=True, destacado=True)[:8],
        'categorias': Categoria.objects.all(),
    })


def catalogo(request):
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    cat = request.GET.get('categoria', '')
    q = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')
    if cat:
        productos = productos.filter(categoria__slug=cat)
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    productos = productos.order_by({'precio': 'precio', '-precio': '-precio'}.get(orden, '-creado'))
    return render(request, 'tienda/catalogo.html', {
        'productos': productos, 'categorias': Categoria.objects.all(),
        'cat': cat, 'q': q, 'orden': orden,
    })


def detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    return render(request, 'tienda/detalle.html', {
        'p': producto, 'variantes': producto.variantes.filter(stock__gt=0),
    })


@require_POST
def carrito_agregar(request):
    variante = get_object_or_404(
        Variante.objects.select_related('producto__categoria'), pk=request.POST.get('variante'))
    try:
        cantidad = max(1, int(request.POST.get('cantidad', 1)))
    except ValueError:
        cantidad = 1

    dorsal = nombre = ''
    if request.POST.get('personalizar'):
        if not variante.producto.categoria.permite_personalizacion:
            messages.error(request, 'Este producto no permite personalización.')
            return redirect('detalle', pk=variante.producto_id)
        dorsal = request.POST.get('dorsal', '').strip()
        nombre = ' '.join(request.POST.get('nombre_bordado', '').split()).upper()
        error = None
        if dorsal and not (dorsal.isascii() and dorsal.isdigit() and 0 <= int(dorsal) <= 99):
            error = 'El dorsal debe ser un número del 0 al 99.'
        elif nombre and not NOMBRE_BORDADO.match(nombre):
            error = 'El nombre puede tener hasta 12 letras (sin números ni símbolos).'
        elif not dorsal and not nombre:
            error = 'Escribe el dorsal, el nombre o ambos; o desactiva la personalización.'
        if error:
            messages.error(request, error)
            return redirect('detalle', pk=variante.producto_id)
        if dorsal:
            dorsal = str(int(dorsal))      # quita ceros a la izquierda

    if variante.stock < 1:
        messages.error(request, 'Esa talla está agotada.')
    else:
        Carrito(request).agregar(variante, cantidad, dorsal, nombre)
        messages.success(request, f'{variante.producto.nombre} (talla {variante.talla}) agregado al carrito.')
    return redirect('carrito')


@require_POST
def carrito_quitar(request, clave):
    Carrito(request).quitar(clave)
    return redirect('carrito')


def carrito_ver(request):
    c = Carrito(request)
    return render(request, 'tienda/carrito.html', {'items': list(c), 'total': c.total()})


@login_required
@sensitive_post_parameters('numero_tarjeta', 'cvv', 'vencimiento')
def checkout(request):
    carrito = Carrito(request)
    items = list(carrito)
    if not items:
        messages.info(request, 'Tu carrito está vacío.')
        return redirect('catalogo')

    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                ids = [i['variante'].id for i in items]
                bloqueadas = Variante.objects.select_for_update().select_related('producto').in_bulk(ids)
                pedido = Pedido.objects.create(
                    usuario=request.user,
                    direccion=form.cleaned_data['direccion'],
                    latitud=form.cleaned_data['latitud'],
                    longitud=form.cleaned_data['longitud'],
                )
                total = Decimal('0')
                for item in items:
                    v = bloqueadas[item['variante'].id]
                    if v.stock < item['cantidad']:
                        raise ValueError(f'No hay stock suficiente de {v.producto.nombre} (talla {v.talla}).')
                    v.stock -= item['cantidad']
                    v.save(update_fields=['stock'])
                    ItemPedido.objects.create(
                        pedido=pedido, variante=v, cantidad=item['cantidad'],
                        precio_unitario=v.producto.precio,
                        dorsal=int(item['dorsal']) if item['dorsal'] != '' else None,
                        nombre_bordado=item['nombre'],
                        extra_unitario=item['extra'],
                    )
                    total += (v.producto.precio + item['extra']) * item['cantidad']
                # Pago simulado aprobado: se guarda solo marca, últimos 4 dígitos y referencia
                datos = form.cleaned_data
                pedido.total = total
                pedido.estado = 'pagado'
                pedido.tarjeta_marca = pagos.marca_tarjeta(datos['numero_tarjeta'])
                pedido.tarjeta_ultimos4 = datos['numero_tarjeta'][-4:]
                pedido.referencia_pago = pagos.referencia_pago()
                pedido.pagado_en = timezone.now()
                pedido.save(update_fields=['total', 'estado', 'tarjeta_marca', 'tarjeta_ultimos4',
                                           'referencia_pago', 'pagado_en'])
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('carrito')
        carrito.limpiar()
        return redirect('pedido_ok', pk=pedido.pk)

    return render(request, 'tienda/checkout.html', {'form': form, 'items': items, 'total': carrito.total()})


@login_required
def pedido_ok(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    return render(request, 'tienda/pedido_ok.html', {'pedido': pedido})


@login_required
def mis_pedidos(request):
    pedidos = request.user.pedidos.select_related('encuesta').prefetch_related('items__variante__producto')
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})


# ---------------- Rastreo (simulado) ----------------
@login_required
def rastreo(request):
    guia = request.GET.get('guia', '').strip()
    if guia:
        digitos = re.sub(r'\D', '', guia)
        pedido = request.user.pedidos.filter(pk=int(digitos)).first() if digitos else None
        if pedido:
            return redirect('rastreo_detalle', pk=pedido.pk)
        messages.error(request, 'No encontramos un pedido tuyo con ese número de guía.')
    return render(request, 'tienda/rastreo.html', {'pedidos': request.user.pedidos.all(), 'guia': guia})


@login_required
def rastreo_detalle(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.select_related('encuesta').prefetch_related('eventos', 'items__variante__producto'),
        pk=pk, usuario=request.user)
    return render(request, 'tienda/rastreo_detalle.html', {'pedido': pedido, 'pasos': pedido.linea_tiempo()})


# ---------------- Encuesta de satisfacción ----------------
@login_required
def encuesta(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    if pedido.estado != 'entregado':
        messages.info(request, 'Podrás calificar tu pedido cuando sea entregado.')
        return redirect('mis_pedidos')
    if pedido.calificado:
        messages.info(request, 'Ya calificaste este pedido. ¡Gracias!')
        return redirect('mis_pedidos')

    form = EncuestaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            Encuesta.objects.create(pedido=pedido, **form.cleaned_data)
        except IntegrityError:
            messages.info(request, 'Ya calificaste este pedido. ¡Gracias!')
        else:
            messages.success(request, '¡Gracias por tu opinión! Nos ayuda a mejorar.')
        return redirect('mis_pedidos')
    preguntas = [form[nombre] for nombre in EncuestaForm.PREGUNTAS]
    return render(request, 'tienda/encuesta.html', {'pedido': pedido, 'form': form, 'preguntas': preguntas})


# ---------------- Chat de preguntas y respuestas (solo en memoria) ----------------
@login_required
def chat_sala(request):
    return render(request, 'tienda/chat.html', {'nombre': sala.nombre_visible(request.user)})


@login_required
def chat_mensajes(request):
    try:
        desde = int(request.GET.get('desde', 0))
    except ValueError:
        desde = 0
    return JsonResponse({'arranque': sala.ARRANQUE, 'mensajes': sala.desde(desde)})


@login_required
@require_POST
def chat_enviar(request):
    mensaje = sala.agregar(request.user, request.POST.get('texto', ''))
    if mensaje is None:
        return JsonResponse({'ok': False}, status=400)
    return JsonResponse({'ok': True})
