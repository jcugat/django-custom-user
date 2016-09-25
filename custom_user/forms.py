"""EmailUser forms."""
import django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


class EmailUserCreationForm(forms.ModelForm):

    """A form for creating new users.

    Includes all the required fields, plus a repeated password.

    """

    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:  # noqa: D101
        model = get_user_model()
        fields = ('email',)

    def clean_email(self):
        """Clean form email.

        :return str email: cleaned email
        :raise forms.ValidationError: Email is duplicated

        """
        # Since EmailUser.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            get_user_model()._default_manager.get(email=email)
        except get_user_model().DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        """Check that the two password entries match.

        :return str password2: cleaned password2
        :raise forms.ValidationError: password2 != password1

        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        """Save user.

        Save the provided password in hashed format.

        :return custom_user.models.EmailUser: user

        """
        user = super(EmailUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmailUserChangeForm(forms.ModelForm):

    """A form for updating users.

    Includes all the fields on the user, but replaces the password field
    with admin's password hash display field.

    """

    # In Django 1.9 the url for changing the password was changed (#15779)
    # A url name was also added in 1.9 (same issue #15779),
    # so reversing the url is not possible for Django < 1.9
    password = ReadOnlyPasswordHashField(label=_("Password"), help_text=_(
        "Raw passwords are not stored, so there is no way to see "
        "this user's password, but you can change the password "
        "using <a href=\"%(url)s\">this form</a>."
    ) % {'url': 'password/' if django.VERSION < (1, 9) else '../password/'})

    class Meta:  # noqa: D101
        model = get_user_model()
        exclude = ()

    def __init__(self, *args, **kwargs):
        """Init the form."""
        super(EmailUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        """Clean password.

        Regardless of what the user provides, return the initial value.
        This is done here, rather than on the field, because the
        field does not have access to the initial value.

        :return str password:

        """
        return self.initial["password"]
