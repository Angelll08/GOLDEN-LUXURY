from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Max, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from analitica.models import Acceso, Metrica
from cuentas.models import Usuario
from tienda.models import Encuesta, ImagenProducto, ItemPedido, Pedido, Producto

from .forms import ProductoForm, VarianteFormSet

solo_admin = user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='login')


@solo_admin
def dashboard(request):
    dinero = DecimalField(max_digits=12, decimal_places=2)
    ventas_cat = list(
        ItemPedido.objects
        .values('variante__producto__categoria__nombre')
        .annotate(total=Sum(ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=dinero)))
        .order_by('-total')
    )
    top_paginas = list(
        Metrica.objects.filter(tipo='vista').values('pagina').annotate(n=Count('id')).order_by('-n')[:8]
    )
    tiempo = list(
        Metrica.objects.filter(tipo='tiempo_pagina').values('pagina')
        .annotate(prom=Avg('segundos')).order_by('-prom')[:8]
    )
    enc = Encuesta.objects.aggregate(
        n=Count('id'), calidad=Avg('calidad'), coincidencia=Avg('coincidencia'),
        entrega=Avg('entrega'), experiencia=Avg('experiencia'), recomendacion=Avg('recomendacion'),
    )
    comentarios = Encuesta.objects.exclude(comentario='').select_related('pedido__usuario')[:5]
    ctx = {
        'enc': enc,
        'comentarios': comentarios,
        'total_ventas': Pedido.objects.aggregate(s=Sum('total'))['s'] or 0,
        'n_pedidos': Pedido.objects.count(),
        'n_usuarios': Usuario.objects.count(),
        'n_productos': Producto.objects.count(),
        'top_paginas': top_paginas,
        'tiempo': tiempo,
        'grafica_paginas': {
            'labels': [t['pagina'] for t in top_paginas],
            'data': [t['n'] for t in top_paginas],
        },
        'grafica_ventas': {
            'labels': [v['variante__producto__categoria__nombre'] for v in ventas_cat],
            'data': [float(v['total'] or 0) for v in ventas_cat],
        },
    }
    return render(request, 'panel/dashboard.html', ctx)


@solo_admin
def productos(request):
    return render(request, 'panel/productos.html', {
        'productos': Producto.objects.select_related('categoria').prefetch_related('variantes'),
    })


@solo_admin
def producto_editar(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    formset = VarianteFormSet(request.POST or None, instance=producto)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        producto = form.save()
        formset.instance = producto
        formset.save()

        # Quitar imágenes de galería marcadas
        ids = [i for i in request.POST.getlist('borrar_imagenes') if i.isdigit()]
        if ids:
            producto.imagenes.filter(pk__in=ids).delete()

        # Agregar las nuevas imágenes (una o varias)
        orden = producto.imagenes.aggregate(m=Max('orden'))['m'] or 0
        for archivo in form.cleaned_data.get('imagenes_extra') or []:
            orden += 1
            ImagenProducto.objects.create(producto=producto, imagen=archivo, orden=orden)

        messages.success(request, 'Producto guardado.')
        return redirect('panel_productos')
    return render(request, 'panel/producto_form.html', {'form': form, 'formset': formset, 'producto': producto})


@solo_admin
@require_POST
def producto_borrar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    try:
        producto.delete()
        messages.success(request, 'Producto eliminado.')
    except Exception:
        # tiene pedidos asociados: mejor desactivarlo
        producto.activo = False
        producto.save(update_fields=['activo'])
        messages.warning(request, 'Tiene pedidos asociados, así que se desactivó en lugar de borrarse.')
    return redirect('panel_productos')


@solo_admin
def pedidos(request):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=request.POST.get('pedido'))
        estado = request.POST.get('estado')
        if estado in dict(Pedido.ESTADOS):
            pedido.estado = estado
            pedido.save(update_fields=['estado'])
            messages.success(request, f'Pedido #{pedido.pk} actualizado.')
        return redirect('panel_pedidos')
    return render(request, 'panel/pedidos.html', {
        'pedidos': Pedido.objects.select_related('usuario').prefetch_related('items__variante__producto'),
        'estados': Pedido.ESTADOS,
    })


@solo_admin
def accesos(request):
    return render(request, 'panel/accesos.html', {'accesos': Acceso.objects.select_related('usuario')[:200]})


@solo_admin
def ubicaciones(request):
    puntos = [
        {'lat': p.latitud, 'lng': p.longitud, 'texto': f'Pedido #{p.pk} · {p.usuario.username} · {p.direccion}'}
        for p in Pedido.objects.select_related('usuario').filter(latitud__isnull=False, longitud__isnull=False)
    ]
    return render(request, 'panel/ubicaciones.html', {'puntos': puntos})
