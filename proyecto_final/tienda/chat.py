"""Chat de preguntas y respuestas SOLO en memoria.

Nada se guarda en la base de datos: los mensajes viven en esta lista y se pierden cuando
se reinicia el servidor (igual que el chat del proyecto PHP)."""
import threading
import time
import uuid
from collections import deque

from django.utils import timezone

MAX_MENSAJES = 200        # solo se conservan los últimos
MAX_CARACTERES = 300
ESPERA_SEGUNDOS = 0.8     # evita que alguien mande mensajes a toda velocidad

ARRANQUE = uuid.uuid4().hex   # cambia en cada reinicio: el navegador lo usa para limpiar su pantalla

_lock = threading.Lock()
_mensajes = deque(maxlen=MAX_MENSAJES)
_ultimo_envio = {}
_siguiente_id = 1


def nombre_visible(usuario):
    """Nombre del perfil: el nombre si lo tiene, si no el usuario."""
    return (usuario.first_name or '').strip() or usuario.username


def agregar(usuario, texto):
    global _siguiente_id
    texto = ' '.join((texto or '').split())[:MAX_CARACTERES]
    if not texto:
        return None
    ahora = time.monotonic()
    with _lock:
        if ahora - _ultimo_envio.get(usuario.pk, 0) < ESPERA_SEGUNDOS:
            return None
        _ultimo_envio[usuario.pk] = ahora
        mensaje = {
            'id': _siguiente_id,
            'usuario': nombre_visible(usuario),
            'staff': bool(usuario.is_staff),
            'texto': texto,
            'hora': timezone.localtime().strftime('%H:%M'),
        }
        _siguiente_id += 1
        _mensajes.append(mensaje)
        return mensaje


def desde(ultimo_id):
    with _lock:
        return [m for m in _mensajes if m['id'] > ultimo_id]
