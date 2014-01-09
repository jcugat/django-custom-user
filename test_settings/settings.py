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
]
SECRET_KEY = 'not_random'
AUTH_USER_MODEL = 'custom_user.EmailUser'