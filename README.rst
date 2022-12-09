Django Custom User
==================

.. image:: https://img.shields.io/pypi/v/django-custom-user.svg
   :target: https://pypi.org/project/django-custom-user/
   :alt: PyPI version

.. image:: https://github.com/jcugat/django-custom-user/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/jcugat/django-custom-user/actions/workflows/ci.yml
   :alt: GitHub Actions Workflow Status (main branch)

.. image:: https://img.shields.io/pypi/dm/django-custom-user.svg
   :target: https://pypi.python.org/pypi/django-custom-user


Custom user model for Django with the same behaviour as the default User class but without a username field. Uses email as the USERNAME_FIELD for authentication.


Quick start
-----------

1. Install django-custom-user with your favorite Python package manager:

.. code-block::

    pip install django-custom-user


2. Add ``'custom_user'`` to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = (
        # other apps
        'custom_user',
    )


3. Set your ``AUTH_USER_MODEL`` setting to use ``EmailUser``:

.. code-block:: python

    AUTH_USER_MODEL = 'custom_user.EmailUser'


4. Create the database tables:

.. code-block::

    python manage.py migrate


Usage
-----

Instead of referring to ``EmailUser`` directly, you should reference the user model using ``get_user_model()`` as explained in the `Django documentation`_. For example:

.. _Django documentation: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model

.. code-block:: python

    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(email="user@example.com")


When you define a foreign key or many-to-many relations to the ``EmailUser`` model, you should specify the custom model using the ``AUTH_USER_MODEL`` setting. For example:

.. code-block:: python

    from django.conf import settings
    from django.db import models

    class Article(models.Model):
        author = models.ForeignKey(settings.AUTH_USER_MODEL)


Extending EmailUser model
-------------------------

You can easily extend ``EmailUser`` by inheriting from ``AbstractEmailUser``. For example:

.. code-block:: python

    from custom_user.models import AbstractEmailUser

    class MyCustomEmailUser(AbstractEmailUser):
        """
        Example of an EmailUser with a new field date_of_birth
        """
        date_of_birth = models.DateField()

Remember to change the ``AUTH_USER_MODEL`` setting to your new class:

.. code-block:: python

    AUTH_USER_MODEL = 'my_app.MyCustomEmailUser'

If you use the AdminSite, add the following code to your ``my_app/admin.py`` file:

.. code-block:: python

    from django.contrib import admin
    from custom_user.admin import EmailUserAdmin
    from .models import MyCustomEmailUser


    class MyCustomEmailUserAdmin(EmailUserAdmin):
        """
        You can customize the interface of your model here.
        """
        pass

    # Register your models here.
    admin.site.register(MyCustomEmailUser, MyCustomEmailUserAdmin)


Supported versions
------------------

Django:

- 3.2 LTS
- 4.0

Python:

- 3.7
- 3.8
- 3.9
- 3.10


Changelog
---------

Version 1.1 (2022-12-10)
~~~~~~~~~~~~~~~~~~~~~~~~

Added support for Django 4.1 and Python 3.11.

Version 1.0 (2022-03-29)
~~~~~~~~~~~~~~~~~~~~~~~~

After a long hiatus, this new version brings compatibility with the latest Django and Python versions, among lots of small improvements and cleanups.

- Supported versions:

  - Django: 3.2 LTS, 4.0

  - Python: 3.7, 3.8, 3.9, 3.10

- Import latest code changes from Django 4.0 (`#65 <https://github.com/jcugat/django-custom-user/pull/65>`_):

  - ``EmailUserCreationForm`` does not strip whitespaces in the password fields, to match Django's behavior.

  - ``EmailUserCreationForm`` supports custom password validators configured by ``AUTH_PASSWORD_VALIDATORS``.

  - ``EmailUser.objects.create_superuser()`` allows empty passwords. It will also check that both ``is_staff`` and ``is_superuser`` parameters are ``True`` (if passed). Otherwise, it would create an invalid superuser.

- Internal changes:

  - Moved away from Travis CI to Github Actions.

  - Build system and dependencies managed with `Poetry <https://python-poetry.org/>`_.

  - Code formatted with `black <https://github.com/psf/black>`_ and `isort <https://pycqa.github.io/isort/>`_.

Note that older versions of Django are not supported, but you can use the previous version 0.7 if you need it.

Version 0.7 (2017-01-12)
~~~~~~~~~~~~~~~~~~~~~~~~

- Fixed change password link in EmailUserChangeForm (thanks to Igor Gai and rubengrill)

Version 0.6 (2016-04-03)
~~~~~~~~~~~~~~~~~~~~~~~~

- Added migrations (thanks to everybody for the help).

How to apply the migrations after upgrading:

Django 1.7
++++++++++

For this version just run the following commands.

.. code-block::

    python manage.py migrate custom_user 0001_initial_django17 --fake
    python manage.py migrate custom_user

Django 1.8
++++++++++

This version didn't work without migrations, which means that your migrations will conflict with the new ones included in this version.

If you added the migrations with Django's `MIGRATION_MODULES <https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-MIGRATION_MODULES>`_ setting, delete the folder containing the migration modules and remove the setting from your config.

If you just ran ``python manage.py makemigrations``, the migrations are located inside your system's or virtualenv's ``site-packages`` folder. You can check the location running this command, and then delete the folder ``migrations`` that is inside:

.. code-block::

    python -c "import os; import custom_user; print(os.path.dirname(custom_user.__file__))"

You can check if you have removed the migrations successfully running this command, you shouldn't see the section ``custom_user`` anymore:

.. code-block::

    python manage.py migrate --list

Once the old migrations are gone, run the following command to finish:

.. code-block::

    python manage.py migrate custom_user 0002_initial_django18 --fake

Version 0.5 (2014-09-20)
~~~~~~~~~~~~~~~~~~~~~~~~

- Django 1.7 compatible (thanks to j0hnsmith).
- Custom application verbose_name in AdminSite with AppConfig.

Version 0.4 (2014-03-06)
~~~~~~~~~~~~~~~~~~~~~~~~

- The create_user() and create_superuser() manager methods now accept is_active and is_staff as parameters (thanks to Edil Kratskih).

Version 0.3 (2014-01-17)
~~~~~~~~~~~~~~~~~~~~~~~~

- AdminSite now works when subclassing AbstractEmailUser (thanks to Ivan Virabyan).
- Updated model changes from Django 1.6.1.

Version 0.2 (2013-11-24)
~~~~~~~~~~~~~~~~~~~~~~~~

- Django 1.6 compatible (thanks to Simon Luijk).

Version 0.1 (2013-04-09)
~~~~~~~~~~~~~~~~~~~~~~~~

- Initial release.

