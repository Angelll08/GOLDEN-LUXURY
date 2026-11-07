from django.conf import settings
from django.db import models


class Acceso(models.Model):
    """Equivale a la tabla `accesos` del proyecto PHP."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField()
    navegador = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']


class Metrica(models.Model):
    """Equivale a `user_metrics`: vistas, clics y tiempo en página."""
    session_id = models.CharField(max_length=64)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    pagina = models.CharField(max_length=255)
    tipo = models.CharField(max_length=30)            # vista, clic, tiempo_pagina
    detalle = models.CharField(max_length=255, blank=True)
    segundos = models.PositiveIntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
