from django.contrib import admin
from .models import Categoria, Encuesta, EventoRastreo, ImagenProducto, ItemPedido, Pedido, Producto, Variante


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 3


class ImagenInline(admin.TabularInline):
    model = ImagenProducto
    extra = 3


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'destacado', 'activo')
    list_filter = ('categoria', 'activo', 'destacado')
    search_fields = ('nombre',)
    inlines = [VarianteInline, ImagenInline]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    list_display = ('nombre', 'permite_personalizacion', 'costo_personalizacion')
    list_editable = ('permite_personalizacion', 'costo_personalizacion')


class ItemInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


class EventoInline(admin.TabularInline):
    model = EventoRastreo
    extra = 0
    can_delete = False
    readonly_fields = ('estado', 'fecha')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'total', 'creado')
    list_filter = ('estado',)
    inlines = [ItemInline, EventoInline]


@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    """Solo lectura: las respuestas de los clientes no se pueden alterar."""
    list_display = ('pedido', 'calidad', 'coincidencia', 'entrega', 'experiencia', 'recomendacion', 'creada')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
