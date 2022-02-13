from .settings import *  # NOQA: F403

INSTALLED_APPS += [  # NOQA: F405
    "test_custom_user_subclass",
]
AUTH_USER_MODEL = "test_custom_user_subclass.MyCustomEmailUser"
