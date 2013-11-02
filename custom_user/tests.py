from django.contrib.auth import get_user_model
from django.core import mail
from django.forms.fields import Field
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

from .forms import EmailUserChangeForm, EmailUserCreationForm
from .models import EmailUser


class UserTest(TestCase):

    user_email = 'newuser@localhost.local'
    user_password = '1234'

    def create_user(self):
        """
        Creates and returns a new user with self.user_email as login and self.user_password as password.
        """
        return get_user_model().objects.create_user(self.user_email, self.user_password)

    def test_user_creation(self):
        # Create a new user saving the time frame
        before_creation = timezone.now()
        self.create_user()
        after_creation = timezone.now()

        # Check user exists and email is correct
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].email, self.user_email)

        # Check date_joined, date_modified and last_login dates
        self.assertLess(before_creation, get_user_model().objects.all()[0].date_joined)
        self.assertLess(get_user_model().objects.all()[0].date_joined, after_creation)

        self.assertLess(before_creation, get_user_model().objects.all()[0].last_login)
        self.assertLess(get_user_model().objects.all()[0].last_login, after_creation)

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
        self.assertRaisesMessage(ValueError,
                                 'The given email must be set',
                                  get_user_model().objects.create_user, email='')


@override_settings(USE_TZ=False, PASSWORD_HASHERS=('django.contrib.auth.hashers.SHA1PasswordHasher',))
class EmailUserCreationFormTest(TestCase):

    def setUp(self):
        EmailUser.objects.create_user('testclient@example.com', 'test123')

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
        self.assertEqual(form['email'].errors, [_('Enter a valid email address.')])

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
        self.assertEqual(repr(u), '<EmailUser: jsmith@example.com>')


@override_settings(USE_TZ=False, PASSWORD_HASHERS=('django.contrib.auth.hashers.SHA1PasswordHasher',))
class EmailUserChangeFormTest(TestCase):

    def setUp(self):
        testclient = EmailUser.objects.create_user('testclient@example.com')
        testclient.password = 'sha1$6efc0$f93efe9fd7542f25a7be94871ea45aa95de57161'
        testclient.save()
        EmailUser.objects.create_user('empty_password@example.com')

    def test_username_validity(self):
        user = EmailUser.objects.get(email='testclient@example.com')
        data = {'email': 'not valid'}
        form = EmailUserChangeForm(data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['email'].errors, [_('Enter a valid email address.')])

    def test_unsuable_password(self):
        user = EmailUser.objects.get(email='empty_password@example.com')
        user.set_unusable_password()
        user.save()
        form = EmailUserChangeForm(instance=user)
        self.assertIn(_("No password set."), form.as_table())

    def test_bug_19133(self):
        "The change form does not return the password value"
        # Use the form to construct the POST data
        user = EmailUser.objects.get(email='testclient@example.com')
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
        user = EmailUser.objects.get(email='testclient@example.com')
        form = EmailUserChangeForm(data={}, instance=user)
        # When rendering the bound password field,
        # ReadOnlyPasswordHashWidget needs the initial
        # value to render correctly
        self.assertEqual(form.initial['password'], form['password'].value())
