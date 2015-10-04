from .settings import *

INSTALLED_APPS += [
    'test_custom_user_subclass',
]
AUTH_USER_MODEL = 'test_custom_user_subclass.MyCustomEmailUser'
