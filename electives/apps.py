from django.apps import AppConfig


class ElectivesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'electives'

    def ready(self):
        # Register signals when app is ready
        import electives.signals  # noqa
