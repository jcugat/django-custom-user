from custom_user.apps import CustomUserConfig


class CustomUserSubclassConfig(CustomUserConfig):
    name = 'test_custom_user_subclass'
    verbose_name = "Test Custom User Subclass"
