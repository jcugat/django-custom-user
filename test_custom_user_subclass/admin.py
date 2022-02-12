from django.contrib import admin
from custom_user.admin import EmailUserAdmin
from .models import MyCustomEmailUser


class MyCustomEmailUserAdmin(EmailUserAdmin):
    pass

# Register your models here.
admin.site.register(MyCustomEmailUser, MyCustomEmailUserAdmin)
