from custom_user.models import AbstractEmailUser


class MyCustomEmailUser(AbstractEmailUser):

    class Meta(AbstractEmailUser.Meta):
        verbose_name = "MyCustomEmailUserVerboseName"
        verbose_name_plural = "MyCustomEmailUserVerboseNamePlural"
