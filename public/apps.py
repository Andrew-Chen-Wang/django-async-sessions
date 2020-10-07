from django.apps import AppConfig


class PublicConfig(AppConfig):
    name = 'public'

    def ready(self):
        try:
            import public.signals  # noqa F401
        except ImportError:
            pass
