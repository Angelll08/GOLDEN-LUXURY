def obtener_ip(request):
    """IP real del visitante (equivale a ip.php; considera proxies)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')
    return ip or '0.0.0.0'
