"""EmailUser tests."""
import os
import re
from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.core import mail, management
from django.forms.fields import Field
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from .forms import EmailUserChangeForm, EmailUserCreationForm


class UserTest(TestCase):

    user_email = "newuser@localhost.local"
    user_password = "1234"

    def create_user(self):
        """
        Create and return a new user with self.user_email as login and
        self.user_password as password.
        """
        return get_user_model().objects.create_user(self.user_email, self.user_password)

    def test_user_creation(self):
        # Create a new user saving the time frame
        right_now = timezone.now().replace(
            microsecond=0
        )  # MySQL doesn't store microseconds
        with mock.patch.object(timezone, "now", return_value=right_now):
            self.create_user()

        # Check user exists and email is correct
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].email, self.user_email)

        # Check date_joined and last_login dates
        self.assertEqual(get_user_model().objects.all()[0].date_joined, right_now)
        self.assertEqual(get_user_model().objects.all()[0].last_login, right_now)

        # Check flags
        self.assertTrue(get_user_model().objects.all()[0].is_active)
        self.assertFalse(get_user_model().objects.all()[0].is_staff)
        self.assertFalse(get_user_model().objects.all()[0].is_superuser)

    def test_user_get_full_name(self):
        user = self.create_user()
        self.assertEqual(user.get_full_name(), self.user_email)

    def test_user_get_short_name(self):
        user = self.create_user()
        self.assertEqual(user.get_short_name(), self.user_email)

    def test_email_user(self):
        # Email definition
        subject = "Email Subject"
        message = "Email Message"
        from_email = "from@normal.com"

        user = self.create_user()

        # Test that no message exists
        self.assertEqual(len(mail.outbox), 0)

        # Send test email
        user.email_user(subject, message, from_email)

        # Test that one message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the email is correct
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, message)
        self.assertEqual(mail.outbox[0].from_email, from_email)
        self.assertEqual(mail.outbox[0].to, [user.email])

    def test_email_user_kwargs(self):
        # valid send_mail parameters
        kwargs = {
            "fail_silently": False,
            "auth_user": None,
            "auth_password": None,
            "connection": None,
        }
        user = get_user_model()(email="foo@bar.com")
        user.email_user(
            subject="Subject here",
            message="This is a message",
            from_email="from@domain.com",
            **kwargs
        )
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        # Verify that test email contains the correct attributes:
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Subject here")
        self.assertEqual(message.body, "This is a message")
        self.assertEqual(message.from_email, "from@domain.com")
        self.assertEqual(message.to, [user.email])


class UserManagerTest(TestCase):
    def test_create_user(self):
        email_lowercase = "normal@normal.com"
        user = get_user_model().objects.create_user(email_lowercase)
        self.assertEqual(user.email, email_lowercase)
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_is_staff(self):
        email_lowercase = "normal@normal.com"
        user = get_user_model().objects.create_user(email_lowercase, is_staff=True)
        self.assertEqual(user.email, email_lowercase)
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        email_lowercase = "normal@normal.com"
        password = "password1234$%&/"
        user = get_user_model().objects.create_superuser(email_lowercase, password)
        self.assertEqual(user.email, email_lowercase)
        self.assertTrue(user.check_password, password)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_super_user_raises_error_on_false_is_superuser(self):
        with self.assertRaisesMessage(
            ValueError, "Superuser must have is_superuser=True."
        ):
            get_user_model().objects.create_superuser(
                email="test@test.com",
                is_superuser=False,
            )

    def test_create_superuser_raises_error_on_false_is_staff(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            get_user_model().objects.create_superuser(
                email="test@test.com",
                is_staff=False,
            )

    def test_user_creation_is_active(self):
        # Create deactivated user
        email_lowercase = "normal@normal.com"
        password = "password1234$%&/"
        user = get_user_model().objects.create_user(
            email_lowercase, password, is_active=False
        )
        self.assertFalse(user.is_active)

    def test_user_creation_is_staff(self):
        # Create staff user
        email_lowercase = "normal@normal.com"
        password = "password1234$%&/"
        user = get_user_model().objects.create_user(
            email_lowercase, password, is_staff=True
        )
        self.assertTrue(user.is_staff)

    def test_create_user_email_domain_normalize_rfc3696(self):
        # According to https://tools.ietf.org/html/rfc3696#section-3
        # the "@" symbol can be part of the local part of an email address
        returned = get_user_model().objects.normalize_email(r"Abc\@DEF@EXAMPLE.com")
        self.assertEqual(returned, r"Abc\@DEF@example.com")

    def test_create_user_email_domain_normalize(self):
        returned = get_user_model().objects.normalize_email("normal@DOMAIN.COM")
        self.assertEqual(returned, "normal@domain.com")

    def test_create_user_email_domain_normalize_with_whitespace(self):
        returned = get_user_model().objects.normalize_email(
            r"email\ with_whitespace@D.COM"
        )
        self.assertEqual(returned, r"email\ with_whitespace@d.com")

    def test_empty_username(self):
        self.assertRaisesMessage(
            ValueError,
            "The given email must be set",
            get_user_model().objects.create_user,
            email="",
        )


class MigrationsTest(TestCase):
    def test_makemigrations_no_changes(self):
        with mock.patch("sys.stdout", new_callable=StringIO) as mocked:
            management.call_command("makemigrations", "custom_user", dry_run=True)
        self.assertEqual(
            mocked.getvalue(), "No changes detected in app 'custom_user'\n"
        )


class TestAuthenticationMiddleware(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_email = "test@example.com"
        cls.user_password = "test_password"
        cls.user = get_user_model().objects.create_user(
            cls.user_email, cls.user_password
        )

    def setUp(self):
        self.middleware = AuthenticationMiddleware(lambda req: HttpResponse())
        self.client.force_login(self.user)
        self.request = HttpRequest()
        self.request.session = self.client.session

    def test_changed_password_doesnt_invalidate_session(self):
        # Changing a user's password shouldn't invalidate the session if session
        # verification isn't activated.
        session_key = self.request.session.session_key
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous)

        # After password change, user should remain logged in.
        self.user.set_password("new_password")
        self.user.save()
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(session_key, self.request.session.session_key)

    def test_no_password_change_doesnt_invalidate_session(self):
        self.request.session = self.client.session
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous)

    def test_changed_password_invalidates_session(self):
        # After password change, user should be anonymous
        self.user.set_password("new_password")
        self.user.save()
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertTrue(self.request.user.is_anonymous)
        # session should be flushed
        self.assertIsNone(self.request.session.session_key)


class TestDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.email = "testclient@example.com"
        cls.password = "test123"
        get_user_model().objects.create_user(cls.email, cls.password)

        get_user_model().objects.create(email="empty_password@example.com", password="")
        get_user_model().objects.create(
            email="unmanageable_password@example.com", password="$"
        )
        get_user_model().objects.create(
            email="unknown_password@example.com", password="foo$bar"
        )


class EmailUserCreationFormTest(TestDataMixin, TestCase):
    def test_user_already_exists(self):
        data = {
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["email"].errors,
            [str(form.error_messages["duplicate_email"])],
        )

    def test_invalid_data(self):
        data = {
            "email": "testclient",
            "password1": self.password,
            "password2": self.password,
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        validator = next(
            v
            for v in get_user_model()._meta.get_field("email").validators
            if v.code == "invalid"
        )
        self.assertEqual(form["email"].errors, [str(validator.message)])

    def test_password_verification(self):
        # The verification password is incorrect.
        data = {
            "email": self.email,
            "password1": "test123",
            "password2": "test",
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["password2"].errors, [str(form.error_messages["password_mismatch"])]
        )

    def test_both_passwords(self):
        # One (or both) passwords weren't given
        data = {"email": self.email}
        form = EmailUserCreationForm(data)
        required_error = [str(Field.default_error_messages["required"])]
        self.assertFalse(form.is_valid())
        self.assertEqual(form["password1"].errors, required_error)
        self.assertEqual(form["password2"].errors, required_error)

        data["password2"] = self.password
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["password1"].errors, required_error)
        self.assertEqual(form["password2"].errors, [])

    @mock.patch("django.contrib.auth.password_validation.password_changed")
    def test_success(self, password_changed):
        # The success case.
        data = {
            "email": "jsmith@example.com",
            "password1": self.password,
            "password2": self.password,
        }
        form = EmailUserCreationForm(data)
        self.assertTrue(form.is_valid())
        form.save(commit=False)
        self.assertEqual(password_changed.call_count, 0)
        u = form.save()
        self.assertEqual(password_changed.call_count, 1)
        self.assertEqual(
            repr(u), "<{}: jsmith@example.com>".format(get_user_model().__name__)
        )

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": (
                    "django.contrib.auth.password_validation."
                    "UserAttributeSimilarityValidator"
                )
            },
            {
                "NAME": (
                    "django.contrib.auth.password_validation.MinimumLengthValidator"
                ),
                "OPTIONS": {
                    "min_length": 12,
                },
            },
        ]
    )
    def test_validates_password(self):
        data = {
            "email": "jsmith@example.com",
            "password1": "jsmith",
            "password2": "jsmith",
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form["password2"].errors), 2)
        self.assertIn(
            "The password is too similar to the email address.",
            form["password2"].errors,
        )
        self.assertIn(
            "This password is too short. It must contain at least 12 characters.",
            form["password2"].errors,
        )

    def test_password_whitespace_not_stripped(self):
        data = {
            "email": "jsmith@example.com",
            "password1": "   testpassword   ",
            "password2": "   testpassword   ",
        }
        form = EmailUserCreationForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["password1"], data["password1"])
        self.assertEqual(form.cleaned_data["password2"], data["password2"])

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": (
                    "django.contrib.auth.password_validation."
                    "UserAttributeSimilarityValidator"
                )
            },
        ]
    )
    def test_password_help_text(self):
        form = EmailUserCreationForm()
        self.assertEqual(
            form.fields["password1"].help_text,
            "<ul><li>"
            "Your password can’t be too similar to your other personal information."
            "</li></ul>",
        )

    def test_html_autocomplete_attributes(self):
        form = EmailUserCreationForm()
        tests = (
            ("password1", "new-password"),
            ("password2", "new-password"),
        )
        for field_name, autocomplete in tests:
            with self.subTest(field_name=field_name, autocomplete=autocomplete):
                self.assertEqual(
                    form.fields[field_name].widget.attrs["autocomplete"], autocomplete
                )


class EmailUserChangeFormTest(TestDataMixin, TestCase):
    def test_username_validity(self):
        user = get_user_model().objects.get(email=self.email)
        data = {"email": "not valid"}
        form = EmailUserChangeForm(data, instance=user)
        self.assertFalse(form.is_valid())
        validator = next(
            v
            for v in get_user_model()._meta.get_field("email").validators
            if v.code == "invalid"
        )
        self.assertEqual(form["email"].errors, [str(validator.message)])

    def test_bug_14242(self):
        # A regression test, introduce by adding an optimization for the
        # EmailUserChangeForm.

        class MyUserForm(EmailUserChangeForm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields[
                    "groups"
                ].help_text = "These groups give users different permissions"

            class Meta(EmailUserChangeForm.Meta):
                fields = ("groups",)

        # Just check we can create it
        MyUserForm({})

    def test_unusable_password(self):
        user = get_user_model().objects.get(email="empty_password@example.com")
        user.set_unusable_password()
        user.save()
        form = EmailUserChangeForm(instance=user)
        self.assertIn(_("No password set."), form.as_table())

    def test_bug_17944_empty_password(self):
        user = get_user_model().objects.get(email="empty_password@example.com")
        form = EmailUserChangeForm(instance=user)
        self.assertIn(_("No password set."), form.as_table())

    def test_bug_17944_unmanageable_password(self):
        user = get_user_model().objects.get(email="unmanageable_password@example.com")
        form = EmailUserChangeForm(instance=user)
        self.assertIn(
            _("Invalid password format or unknown hashing algorithm."), form.as_table()
        )

    def test_bug_17944_unknown_password_algorithm(self):
        user = get_user_model().objects.get(email="unknown_password@example.com")
        form = EmailUserChangeForm(instance=user)
        self.assertIn(
            _("Invalid password format or unknown hashing algorithm."), form.as_table()
        )

    def test_bug_19133(self):
        "The change form does not return the password value"
        # Use the form to construct the POST data
        user = get_user_model().objects.get(email=self.email)
        form_for_data = EmailUserChangeForm(instance=user)
        post_data = form_for_data.initial

        # The password field should be readonly, so anything
        # posted here should be ignored; the form will be
        # valid, and give back the 'initial' value for the
        # password field.
        post_data["password"] = "new password"
        form = EmailUserChangeForm(instance=user, data=post_data)

        self.assertTrue(form.is_valid())
        # original hashed password contains $
        self.assertIn("$", form.cleaned_data["password"])

    def test_bug_19349_bound_password_field(self):
        user = get_user_model().objects.get(email=self.email)
        form = EmailUserChangeForm(data={}, instance=user)
        # When rendering the bound password field,
        # ReadOnlyPasswordHashWidget needs the initial
        # value to render correctly
        self.assertEqual(form.initial["password"], form["password"].value())


class EmailUserAdminTest(TestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_password = "test_password"
        self.user = get_user_model().objects.create_superuser(
            self.user_email, self.user_password
        )

        if settings.AUTH_USER_MODEL == "custom_user.EmailUser":
            self.app_name = "custom_user"
            self.model_name = "emailuser"
            self.model_verbose_name = "user"
            self.model_verbose_name_plural = "Users"
            self.app_verbose_name = "Custom User"
        if settings.AUTH_USER_MODEL == "test_custom_user_subclass.MyCustomEmailUser":
            self.app_name = "test_custom_user_subclass"
            self.model_name = "mycustomemailuser"
            self.model_verbose_name = "MyCustomEmailUserVerboseName"
            self.model_verbose_name_plural = "MyCustomEmailUserVerboseNamePlural"
            self.app_verbose_name = "Test Custom User Subclass"

    def test_url(self):
        self.assertTrue(
            self.client.login(
                username=self.user_email,
                password=self.user_password,
            )
        )
        response = self.client.get(reverse("admin:app_list", args=(self.app_name,)))
        self.assertEqual(response.status_code, 200)

    def test_app_name(self):
        self.assertTrue(
            self.client.login(
                username=self.user_email,
                password=self.user_password,
            )
        )

        response = self.client.get(reverse("admin:app_list", args=(self.app_name,)))
        self.assertEqual(response.context["app_list"][0]["name"], self.app_verbose_name)

    def test_model_name(self):
        self.assertTrue(
            self.client.login(
                username=self.user_email,
                password=self.user_password,
            )
        )

        response = self.client.get(
            reverse("admin:%s_%s_changelist" % (self.app_name, self.model_name))
        )
        self.assertEqual(
            str(response.context["title"]),
            "Select %s to change" % self.model_verbose_name,
        )

    def test_model_name_plural(self):
        self.assertTrue(
            self.client.login(
                username=self.user_email,
                password=self.user_password,
            )
        )

        response = self.client.get(reverse("admin:app_list", args=(self.app_name,)))
        self.assertEqual(
            str(response.context["app_list"][0]["models"][0]["name"]),
            self.model_verbose_name_plural,
        )

    def test_user_change_password(self):
        self.assertTrue(
            self.client.login(
                username=self.user_email,
                password=self.user_password,
            )
        )

        user_change_url = reverse(
            "admin:%s_%s_change" % (self.app_name, self.model_name),
            args=(self.user.pk,),
        )
        password_change_url = reverse(
            "admin:auth_user_password_change", args=(self.user.pk,)
        )

        response = self.client.get(user_change_url)
        # Test the link inside password field help_text.
        rel_link = re.search(
            r'you can change the password using <a href="([^"]*)">this form</a>',
            str(response.content),
        ).groups()[0]
        self.assertEqual(
            os.path.normpath(user_change_url + rel_link),
            os.path.normpath(password_change_url),
        )

        # Test url is correct.
        self.assertEqual(
            self.client.get(password_change_url).status_code,
            200,
        )
