from django.apps import AppConfig


class AnaliticaConfig(AppConfig):
    name = 'analitica'

    def ready(self):
        from . import signals  # noqa: F401  (registra la señal de login)
