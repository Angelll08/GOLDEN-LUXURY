"""Pago SIMULADO: no se contacta ningún banco ni se cobra nada.
Acepta cualquier número con formato válido (no se verifica el dígito de control)."""
import re
import secrets

_MASTERCARD = re.compile(r'^(5[1-5]|222[1-9]|22[3-9]\d|2[3-6]\d\d|27[01]\d|2720)')


def marca_tarjeta(numero):
    if numero.startswith('4'):
        return 'Visa'
    if _MASTERCARD.match(numero):
        return 'Mastercard'
    if re.match(r'^3[47]', numero):
        return 'American Express'
    return 'Tarjeta'


def referencia_pago():
    return 'PAY-' + secrets.token_hex(5).upper()
