import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Metrica

TIPOS = {'vista', 'clic', 'tiempo_pagina'}


@require_POST
def evento(request):
    try:
        d = json.loads(request.body)
        tipo = str(d.get('action_type', ''))
        if tipo not in TIPOS:
            return JsonResponse({'status': 'ignorado'}, status=400)
        Metrica.objects.create(
            session_id=str(d.get('session_id', 'desconocido'))[:64],
            usuario=request.user if request.user.is_authenticated else None,
            pagina=str(d.get('page', ''))[:255],
            tipo=tipo,
            detalle=str(d.get('element_details') or '')[:255],
            segundos=max(0, int(d.get('time_spent', 0))),
        )
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'success'})
