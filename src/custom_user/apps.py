"""App configuration for custom_user."""
from django.apps import AppConfig


class CustomUserConfig(AppConfig):

    """Default configuration for custom_user."""

    name = "custom_user"
    verbose_name = "Custom User"

    # https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
    default_auto_field = "django.db.models.AutoField"
