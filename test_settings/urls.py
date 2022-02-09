import django
from django.contrib import admin

if django.VERSION < (2, 0):
    from django.conf.urls import include, url as re_path
else:
    from django.urls import include, re_path

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', include(admin.site.urls)),
]
