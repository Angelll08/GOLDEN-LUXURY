from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Cliente de la tienda. is_staff=True => administrador."""
    telefono = models.CharField(max_length=20, blank=True)
