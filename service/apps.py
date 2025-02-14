from django.apps import AppConfig

class ServiceConfig(AppConfig):
    name = 'service'
    
    def ready(self):
        import service.signals.entitlement_handlers
        # Ensure admin modules are loaded
        from . import admin  # noqa
