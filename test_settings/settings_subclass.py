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
    'django.contrib.sessions',
    'custom_user',
    'test_custom_user_subclass',
]
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)
SECRET_KEY = 'not_random'
AUTH_USER_MODEL = 'test_custom_user_subclass.MyCustomEmailUser'
