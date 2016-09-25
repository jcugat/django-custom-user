"""EmailUser tests."""
from mock import patch
import os
import re
from unittest import skipIf, skipUnless

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.core import mail
from django.core import management
from django.core.urlresolvers import reverse
from django.db import connection
from django.forms.fields import Field
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

from .forms import EmailUserChangeForm, EmailUserCreationForm

try:
    from django.contrib.auth.middleware import SessionAuthenticationMiddleware
except ImportError:
    # Only available from Django 1.7, ignore the tests otherwise
    SessionAuthenticationMiddleware = None


class UserTest(TestCase):

    user_email = 'newuser@localhost.local'
    user_password = '1234'

    def create_user(self):
        """Create and return a new user with self.user_email as login and self.user_password as password."""
        return get_user_model().objects.create_user(self.user_email, self.user_password)

    def test_user_creation(self):
        # Create a new user saving the time frame
        right_now = timezone.now().replace(microsecond=0)  # MySQL doesn't store microseconds
        with patch.object(timezone, 'now', return_value=right_now):
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
        from_email = 'from@normal.com'

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
        user = get_user_model()(email='foo@bar.com')
        user.email_user(
            subject="Subject here",
            message="This is a message", from_email="from@domain.com", **kwargs)
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
        email_lowercase = 'normal@normal.com'
        user = get_user_model().objects.create_user(email_lowercase)
        self.assertEqual(user.email, email_lowercase)
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        email_lowercase = 'normal@normal.com'
        password = 'password1234$%&/'
        user = get_user_model().objects.create_superuser(email_lowercase, password)
        self.assertEqual(user.email, email_lowercase)
        self.assertTrue(user.check_password, password)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_creation_is_active(self):
        # Create deactivated user
        email_lowercase = 'normal@normal.com'
        password = 'password1234$%&/'
        user = get_user_model().objects.create_user(email_lowercase, password, is_active=False)
        self.assertFalse(user.is_active)

    def test_user_creation_is_staff(self):
        # Create staff user
        email_lowercase = 'normal@normal.com'
        password = 'password1234$%&/'
        user = get_user_model().objects.create_user(email_lowercase, password, is_staff=True)
        self.assertTrue(user.is_staff)

    def test_create_user_email_domain_normalize_rfc3696(self):
        # According to http://tools.ietf.org/html/rfc3696#section-3
        # the "@" symbol can be part of the local part of an email address
        returned = get_user_model().objects.normalize_email(r'Abc\@DEF@EXAMPLE.com')
        self.assertEqual(returned, r'Abc\@DEF@example.com')

    def test_create_user_email_domain_normalize(self):
        returned = get_user_model().objects.normalize_email('normal@DOMAIN.COM')
        self.assertEqual(returned, 'normal@domain.com')

    def test_create_user_email_domain_normalize_with_whitespace(self):
        returned = get_user_model().objects.normalize_email('email\ with_whitespace@D.COM')
        self.assertEqual(returned, 'email\ with_whitespace@d.com')

    def test_empty_username(self):
        self.assertRaisesMessage(
            ValueError,
            'The given email must be set',
            get_user_model().objects.create_user, email=''
        )


@skipIf(django.VERSION < (1, 7, 0), 'Migrations not available in this Django version')
class MigrationsTest(TestCase):

    def test_makemigrations_no_changes(self):
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO

        with patch('sys.stdout', new_callable=StringIO) as mock:
            management.call_command('makemigrations', 'custom_user', dry_run=True)
        self.assertEqual(mock.getvalue(), 'No changes detected in app \'custom_user\'\n')

    @skipUnless(django.VERSION[:2] == (1, 7), 'Monkey patch only applied to Django 1.7')
    def test_monkey_patch_model_field(self):
        field_last_login = get_user_model()._meta.get_field('last_login')
        self.assertTrue(field_last_login.null)
        self.assertTrue(field_last_login.blank)

    @skipUnless(django.VERSION[:2] == (1, 7), 'Monkey patch only applied to Django 1.7')
    def test_monkey_patch_db_column(self):
        table_name = get_user_model()._meta.db_table
        cursor = connection.cursor()
        table_fields = connection.introspection.get_table_description(cursor, table_name)
        field = next(field for field in table_fields if field.name == 'last_login')
        self.assertTrue(field.null_ok)

    @skipUnless(django.VERSION[:2] == (1, 7), 'Monkey patch only applied to Django 1.7')
    def test_monkey_patch_side_effects(self):
        # Check the parent model isn't affected from the monkey patch
        from django.contrib.auth.models import AbstractBaseUser
        field_last_login = AbstractBaseUser._meta.get_field('last_login')
        self.assertFalse(field_last_login.null)
        self.assertFalse(field_last_login.blank)


@skipIf(SessionAuthenticationMiddleware is None, "SessionAuthenticationMiddleware not available in this version")
class TestSessionAuthenticationMiddleware(TestCase):

    def setUp(self):
        self.user_email = 'test@example.com'
        self.user_password = 'test_password'
        self.user = get_user_model().objects.create_user(
            self.user_email,
            self.user_password)

        self.middleware_auth = AuthenticationMiddleware()
        self.middleware_session_auth = SessionAuthenticationMiddleware()
        self.assertTrue(self.client.login(
            username=self.user_email,
            password=self.user_password,
        ))
        self.request = HttpRequest()
        self.request.session = self.client.session

    def test_changed_password_doesnt_invalidate_session(self):
        # Changing a user's password shouldn't invalidate the session if session
        # verification isn't activated.
        session_key = self.request.session.session_key
        self.middleware_auth.process_request(self.request)
        self.middleware_session_auth.process_request(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous())

        # After password change, user should remain logged in.
        self.user.set_password('new_password')
        self.user.save()
        self.middleware_auth.process_request(self.request)
        self.middleware_session_auth.process_request(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous())
        self.assertEqual(session_key, self.request.session.session_key)

    def test_changed_password_invalidates_session_with_middleware(self):
        session_key = self.request.session.session_key
        with self.modify_settings(MIDDLEWARE_CLASSES={'append': ['django.contrib.auth.middleware.SessionAuthenticationMiddleware']}):
            # After password change, user should be anonymous
            self.user.set_password('new_password')
            self.user.save()
            self.middleware_auth.process_request(self.request)
            self.middleware_session_auth.process_request(self.request)
            self.assertIsNotNone(self.request.user)
            self.assertTrue(self.request.user.is_anonymous())
        # session should be flushed
        self.assertNotEqual(session_key, self.request.session.session_key)


@override_settings(USE_TZ=False, PASSWORD_HASHERS=('django.contrib.auth.hashers.SHA1PasswordHasher',))
class EmailUserCreationFormTest(TestCase):

    def setUp(self):
        get_user_model().objects.create_user('testclient@example.com', 'test123')

    def test_user_already_exists(self):
        data = {
            'email': 'testclient@example.com',
            'password1': 'test123',
            'password2': 'test123',
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["email"].errors,
                         [force_text(form.error_messages['duplicate_email'])])

    def test_invalid_data(self):
        data = {
            'email': 'testclient',
            'password1': 'test123',
            'password2': 'test123',
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["email"].errors,
                         [_('Enter a valid email address.')])

    def test_password_verification(self):
        # The verification password is incorrect.
        data = {
            'email': 'testclient@example.com',
            'password1': 'test123',
            'password2': 'test',
        }
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["password2"].errors,
                         [force_text(form.error_messages['password_mismatch'])])

    def test_both_passwords(self):
        # One (or both) passwords weren't given
        data = {'email': 'testclient@example.com'}
        form = EmailUserCreationForm(data)
        required_error = [force_text(Field.default_error_messages['required'])]
        self.assertFalse(form.is_valid())
        self.assertEqual(form['password1'].errors, required_error)
        self.assertEqual(form['password2'].errors, required_error)

        data['password2'] = 'test123'
        form = EmailUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['password1'].errors, required_error)
        self.assertEqual(form['password2'].errors, [])

    def test_success(self):
        # The success case.
        data = {
            'email': 'jsmith@example.com',
            'password1': 'test123',
            'password2': 'test123',
        }
        form = EmailUserCreationForm(data)
        self.assertTrue(form.is_valid())
        u = form.save()
        self.assertEqual(repr(u), '<%s: jsmith@example.com>' % get_user_model().__name__)


@override_settings(USE_TZ=False, PASSWORD_HASHERS=('django.contrib.auth.hashers.SHA1PasswordHasher',))
class EmailUserChangeFormTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user('testclient@example.com')
        user.password = 'sha1$6efc0$f93efe9fd7542f25a7be94871ea45aa95de57161'
        user.save()
        get_user_model().objects.create_user('empty_password@example.com')
        user_unmanageable = get_user_model().objects.create_user('unmanageable_password@example.com')
        user_unmanageable.password = '$'
        user_unmanageable.save()
        user_unknown = get_user_model().objects.create_user('unknown_password@example.com')
        user_unknown.password = 'foo$bar'
        user_unknown.save()

    def test_username_validity(self):
        user = get_user_model().objects.get(email='testclient@example.com')
        data = {'email': 'not valid'}
        form = EmailUserChangeForm(data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors,
                         [_('Enter a valid email address.')])

    def test_bug_14242(self):
        # A regression test, introduce by adding an optimization for the
        # EmailUserChangeForm.

        class MyUserForm(EmailUserChangeForm):
            def __init__(self, *args, **kwargs):
                super(MyUserForm, self).__init__(*args, **kwargs)
                self.fields['groups'].help_text = 'These groups give users different permissions'

            class Meta(EmailUserChangeForm.Meta):
                fields = ('groups',)

        # Just check we can create it
        MyUserForm({})

    def test_unsuable_password(self):
        user = get_user_model().objects.get(email='empty_password@example.com')
        user.set_unusable_password()
        user.save()
        form = EmailUserChangeForm(instance=user)
        self.assertIn(_("No password set."), form.as_table())

    def test_bug_17944_empty_password(self):
        user = get_user_model().objects.get(email='empty_password@example.com')
        form = EmailUserChangeForm(instance=user)
        self.assertIn(_("No password set."), form.as_table())

    def test_bug_17944_unmanageable_password(self):
        user = get_user_model().objects.get(email='unmanageable_password@example.com')
        form = EmailUserChangeForm(instance=user)
        self.assertIn(
            _("Invalid password format or unknown hashing algorithm."),
            form.as_table())

    def test_bug_17944_unknown_password_algorithm(self):
        user = get_user_model().objects.get(email='unknown_password@example.com')
        form = EmailUserChangeForm(instance=user)
        self.assertIn(
            _("Invalid password format or unknown hashing algorithm."),
            form.as_table())

    def test_bug_19133(self):
        """The change form does not return the password value."""
        # Use the form to construct the POST data
        user = get_user_model().objects.get(email='testclient@example.com')
        form_for_data = EmailUserChangeForm(instance=user)
        post_data = form_for_data.initial

        # The password field should be readonly, so anything
        # posted here should be ignored; the form will be
        # valid, and give back the 'initial' value for the
        # password field.
        post_data['password'] = 'new password'
        form = EmailUserChangeForm(instance=user, data=post_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['password'], 'sha1$6efc0$f93efe9fd7542f25a7be94871ea45aa95de57161')

    def test_bug_19349_bound_password_field(self):
        user = get_user_model().objects.get(email='testclient@example.com')
        form = EmailUserChangeForm(data={}, instance=user)
        # When rendering the bound password field,
        # ReadOnlyPasswordHashWidget needs the initial
        # value to render correctly
        self.assertEqual(form.initial['password'], form['password'].value())


class EmailUserAdminTest(TestCase):

    def setUp(self):
        self.user_email = 'test@example.com'
        self.user_password = 'test_password'
        self.user = get_user_model().objects.create_superuser(
            self.user_email,
            self.user_password)

        if settings.AUTH_USER_MODEL == "custom_user.EmailUser":
            self.app_name = "custom_user"
            self.model_name = "emailuser"
            self.model_verbose_name = "user"
            self.model_verbose_name_plural = "Users"
            if django.VERSION[:2] < (1, 7):
                self.app_verbose_name = "Custom_User"
            else:
                self.app_verbose_name = "Custom User"
        elif settings.AUTH_USER_MODEL == "test_custom_user_subclass.MyCustomEmailUser":
            self.app_name = "test_custom_user_subclass"
            self.model_name = "mycustomemailuser"
            self.model_verbose_name = "MyCustomEmailUserVerboseName"
            self.model_verbose_name_plural = "MyCustomEmailUserVerboseNamePlural"
            if django.VERSION[:2] < (1, 7):
                self.app_verbose_name = "Test_Custom_User_Subclass"
            else:
                self.app_verbose_name = "Test Custom User Subclass"

    def test_url(self):
        self.assertTrue(self.client.login(
            username=self.user_email,
            password=self.user_password,
        ))
        response = self.client.get(reverse("admin:app_list", args=(self.app_name,)))
        self.assertEqual(response.status_code, 200)

    def test_app_name(self):
        self.assertTrue(self.client.login(
            username=self.user_email,
            password=self.user_password,
        ))

        response = self.client.get(reverse("admin:app_list", args=(self.app_name,)))
        self.assertEqual(response.context['app_list'][0]['name'], self.app_verbose_name)

    def test_model_name(self):
        self.assertTrue(self.client.login(
            username=self.user_email,
            password=self.user_password,
        ))

        response = self.client.get(reverse("admin:%s_%s_changelist" % (self.app_name, self.model_name)))
        self.assertEqual(force_text(response.context['title']), "Select %s to change" % self.model_verbose_name)

    def test_model_name_plural(self):
        self.assertTrue(self.client.login(
            username=self.user_email,
            password=self.user_password,
        ))

        response = self.client.get(reverse("admin:app_list", args=(self.app_name,)))
        self.assertEqual(force_text(response.context['app_list'][0]['models'][0]['name']), self.model_verbose_name_plural)

    def test_user_change_password(self):
        self.assertTrue(self.client.login(
            username=self.user_email,
            password=self.user_password,
        ))

        user_change_url = reverse('admin:%s_%s_change' % (self.app_name, self.model_name), args=(self.user.pk,))

        if django.VERSION[:2] < (1, 8):
            # Since reverse() does not exist yet, create path manually
            password_change_url = user_change_url + 'password/'
        else:
            password_change_url = reverse('admin:auth_user_password_change', args=(self.user.pk,))

        response = self.client.get(user_change_url)
        # Test the link inside password field help_text.
        rel_link = re.search(
            r'you can change the password using <a href="([^"]*)">this form</a>',
            force_text(response.content)
        ).groups()[0]
        self.assertEqual(
            os.path.normpath(user_change_url + rel_link),
            os.path.normpath(password_change_url)
        )

        # Test url is correct.
        self.assertEqual(
            self.client.get(password_change_url).status_code,
            200,
        )
