DEBUG = True
USE_TZ = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'custom_user',
    'test_custom_user_subclass',
]
SECRET_KEY = 'not_random'
AUTH_USER_MODEL = 'test_custom_user_subclass.MyCustomEmailUser'
