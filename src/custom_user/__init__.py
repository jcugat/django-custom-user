"""Custom user model for Django with email instead of username."""

__version__ = '0.7'

try:
    import django

    if django.VERSION < (3, 2):
        default_app_config = 'custom_user.apps.CustomUserConfig'
except ModuleNotFoundError:
    # this part is useful for allow setup.py to be used for version checks
    pass
