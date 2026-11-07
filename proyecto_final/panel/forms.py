from django import forms
from django.forms import inlineformset_factory

from tienda.models import Producto, Variante


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Campo que acepta varias imágenes a la vez (valida que sean imágenes reales)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        limpiar = super().clean
        if isinstance(data, (list, tuple)):
            resultado = [limpiar(d, initial) for d in data]
        else:
            resultado = [limpiar(data, initial)]
        return [r for r in resultado if r]


class ProductoForm(forms.ModelForm):
    imagenes_extra = MultipleImageField(
        required=False,
        label='Más imágenes (puedes seleccionar varias a la vez)',
    )

    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'imagen', 'destacado', 'activo']
        labels = {'imagen': 'Imagen principal (portada)'}


VarianteFormSet = inlineformset_factory(
    Producto, Variante, fields=('talla', 'stock'), extra=3, can_delete=True,
)
