from django.contrib import admin

from .models import Acceso, Metrica


class SoloLectura(admin.ModelAdmin):
    """Las métricas y accesos se generan solos: nadie puede crearlas, editarlas ni borrarlas."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Acceso)
class AccesoAdmin(SoloLectura):
    list_display = ('fecha', 'usuario', 'ip', 'navegador')
    list_filter = ('fecha',)
    search_fields = ('usuario__username', 'ip')


@admin.register(Metrica)
class MetricaAdmin(SoloLectura):
    list_display = ('fecha', 'tipo', 'pagina', 'detalle', 'segundos', 'usuario')
    list_filter = ('tipo', 'fecha')
    search_fields = ('pagina', 'detalle', 'session_id')
