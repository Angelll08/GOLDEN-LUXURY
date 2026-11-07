from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=60)          # Jerseys, Tenis, Uniformes...
    slug = models.SlugField(unique=True)
    permite_personalizacion = models.BooleanField(
        'Permite dorsal y nombre bordado', default=False,
        help_text='Actívalo solo en Jerseys y Uniformes.')
    costo_personalizacion = models.DecimalField(
        'Costo extra del bordado (por pieza)', max_digits=8, decimal_places=2, default=150,
        help_text='Se suma al precio de cada playera personalizada.')

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return self.nombre


class ImagenProducto(models.Model):
    """Imágenes extra (galería) de un producto. La portada sigue siendo Producto.imagen."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/galeria/')
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return f'Imagen de {self.producto.nombre}'


class Variante(models.Model):
    """Talla con su propio stock."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    talla = models.CharField(max_length=10)           # S, M, L, 26, 27...
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'talla')

    def __str__(self):
        return f'{self.producto.nombre} - {self.talla}'


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('preparando', 'Preparando'),
        ('enviado', 'Enviado'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
    ]
    # Texto de cada paso del rastreo (simulado)
    PASOS = {
        'pendiente': ('Pedido recibido', 'Recibimos tu pedido y esperamos la confirmación del pago.'),
        'pagado': ('Pago confirmado', 'Tu pago fue confirmado.'),
        'preparando': ('Preparando tu pedido', 'Estamos empacando tus productos (y bordándolos, si los personalizaste).'),
        'enviado': ('Enviado', 'Tu paquete salió de nuestro almacén con Golden Express.'),
        'en_camino': ('En camino', 'Tu paquete está en reparto y llegará pronto a tu dirección.'),
        'entregado': ('Entregado', '¡Tu pedido fue entregado! Esperamos que lo disfrutes.'),
    }
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos')
    estado = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    direccion = models.CharField(max_length=255)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado = models.DateTimeField(auto_now_add=True)
    # Pago simulado: solo se guarda la marca, los últimos 4 dígitos y una referencia
    tarjeta_marca = models.CharField(max_length=20, blank=True)
    tarjeta_ultimos4 = models.CharField(max_length=4, blank=True)
    referencia_pago = models.CharField(max_length=20, blank=True)
    pagado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estado_previo = self.estado

    def save(self, *args, **kwargs):
        """Cada vez que cambia el estado se guarda un evento para la línea de tiempo del rastreo."""
        cambio = self._state.adding or self._estado_previo != self.estado
        super().save(*args, **kwargs)
        if cambio:
            EventoRastreo.objects.create(pedido=self, estado=self.estado)
        self._estado_previo = self.estado

    def __str__(self):
        return f'Pedido #{self.pk}'

    @property
    def guia(self):
        return f'GL{self.pk:08d}MX'

    @property
    def entrega_estimada(self):
        return timezone.localtime(self.creado).date() + timedelta(days=5)

    @property
    def indice_estado(self):
        return [e for e, _ in self.ESTADOS].index(self.estado)

    @property
    def progreso(self):
        return int(self.indice_estado / (len(self.ESTADOS) - 1) * 100)

    @property
    def calificado(self):
        return hasattr(self, 'encuesta')

    def linea_tiempo(self):
        fechas = {ev.estado: ev.fecha for ev in self.eventos.all()}
        actual = self.indice_estado
        pasos = []
        for i, (clave, _) in enumerate(self.ESTADOS):
            titulo, descripcion = self.PASOS[clave]
            fecha = fechas.get(clave) or (self.creado if clave == 'pendiente' else None)
            pasos.append({'clave': clave, 'titulo': titulo, 'descripcion': descripcion,
                          'hecho': i <= actual, 'actual': i == actual, 'fecha': fecha})
        return pasos


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    variante = models.ForeignKey(Variante, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # Personalización (bordado)
    dorsal = models.PositiveSmallIntegerField(null=True, blank=True)
    nombre_bordado = models.CharField(max_length=20, blank=True)
    extra_unitario = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    @property
    def personalizado(self):
        return self.dorsal is not None or bool(self.nombre_bordado)

    @property
    def subtotal(self):
        return self.cantidad * (self.precio_unitario + self.extra_unitario)


class EventoRastreo(models.Model):
    """Historial de estados de un pedido (alimenta la línea de tiempo del rastreo)."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='eventos')
    estado = models.CharField(max_length=12)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'id']


def _calificacion():
    return models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class Encuesta(models.Model):
    """Encuesta de satisfacción de un pedido entregado (1 a 5 en cada pregunta)."""
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='encuesta')
    calidad = _calificacion()
    coincidencia = _calificacion()
    entrega = _calificacion()
    experiencia = _calificacion()
    recomendacion = _calificacion()
    comentario = models.TextField(blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada']

    def __str__(self):
        return f'Encuesta del pedido #{self.pedido_id}'
