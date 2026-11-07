from django.conf import settings


def _listo(proveedor):
    app = settings.SOCIALACCOUNT_PROVIDERS.get(proveedor, {}).get('APP', {})
    cid = app.get('client_id', '')
    secreto = app.get('secret', '')
    return bool(cid) and bool(secreto) and not cid.startswith('PON_AQUI') and not secreto.startswith('PON_AQUI')


def social(request):
    """Indica qué botones de redes sociales ya tienen credenciales configuradas."""
    return {'google_listo': _listo('google'), 'facebook_listo': _listo('facebook')}
