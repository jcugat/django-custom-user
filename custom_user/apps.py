"""App configuration for custom_user."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .signals import remove_empty_migration_on_django_17


class CustomUserConfig(AppConfig):

    """Default configuration for custom_user."""

    name = 'custom_user'
    verbose_name = "Custom User"

    def ready(self):
        post_migrate.connect(remove_empty_migration_on_django_17, sender=self)
