import re

from django import forms


class CheckoutForm(forms.Form):
    direccion = forms.CharField(label='Dirección de envío', max_length=255)
    latitud = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitud = forms.FloatField(required=False, widget=forms.HiddenInput)

    # Pago simulado con tarjeta
    titular = forms.CharField(label='Nombre del titular', max_length=60,
                              widget=forms.TextInput(attrs={'autocomplete': 'cc-name', 'placeholder': 'Como aparece en la tarjeta'}))
    numero_tarjeta = forms.CharField(label='Número de tarjeta', max_length=23,
                                     widget=forms.TextInput(attrs={'autocomplete': 'cc-number', 'inputmode': 'numeric',
                                                                   'placeholder': '4242 4242 4242 4242'}))
    vencimiento = forms.CharField(label='Vencimiento', max_length=5,
                                  widget=forms.TextInput(attrs={'autocomplete': 'cc-exp', 'inputmode': 'numeric', 'placeholder': 'MM/AA'}))
    cvv = forms.CharField(label='CVV', max_length=4,
                          widget=forms.PasswordInput(attrs={'autocomplete': 'cc-csc', 'inputmode': 'numeric', 'placeholder': '123'}))

    def clean_titular(self):
        titular = ' '.join(self.cleaned_data['titular'].split())
        if len(titular) < 3:
            raise forms.ValidationError('Escribe el nombre como aparece en la tarjeta.')
        return titular

    def clean_numero_tarjeta(self):
        digitos = re.sub(r'[\s-]', '', self.cleaned_data['numero_tarjeta'])
        if not (digitos.isascii() and digitos.isdigit() and 13 <= len(digitos) <= 19):
            raise forms.ValidationError('Escribe un número de tarjeta de 13 a 19 dígitos.')
        return digitos

    def clean_vencimiento(self):
        valor = self.cleaned_data['vencimiento'].replace(' ', '')
        if not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', valor):
            raise forms.ValidationError('Usa el formato MM/AA, por ejemplo 08/29.')
        return valor

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv'].strip()
        if not (cvv.isascii() and cvv.isdigit() and 3 <= len(cvv) <= 4):
            raise forms.ValidationError('El CVV tiene 3 o 4 dígitos.')
        return cvv


ESCALA = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]


def _pregunta(texto, ayuda='1 = Muy mal · 5 = Excelente'):
    return forms.TypedChoiceField(label=texto, choices=ESCALA, coerce=int,
                                  widget=forms.RadioSelect, help_text=ayuda)


class EncuestaForm(forms.Form):
    PREGUNTAS = ['calidad', 'coincidencia', 'entrega', 'experiencia', 'recomendacion']

    calidad = _pregunta('1. ¿Qué tan satisfecho estás con la calidad del producto?',
                        '1 = Muy insatisfecho · 5 = Muy satisfecho')
    coincidencia = _pregunta('2. ¿El producto fue como lo viste en la página?',
                             '1 = Nada parecido · 5 = Idéntico')
    entrega = _pregunta('3. ¿Cómo calificas el tiempo y el estado en que llegó tu pedido?')
    experiencia = _pregunta('4. ¿Qué tal fue tu experiencia comprando en el sitio (catálogo, carrito, pago)?')
    recomendacion = _pregunta('5. ¿Qué tan probable es que recomiendes Golden Luxury a un amigo?',
                              '1 = Nada probable · 5 = Muy probable')
    comentario = forms.CharField(label='Comentarios (opcional)', required=False, max_length=500,
                                 widget=forms.Textarea(attrs={'rows': 3}))
