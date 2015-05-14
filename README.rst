Django Custom User
==================

.. image:: https://img.shields.io/pypi/v/django-custom-user.svg
    :target: https://pypi.python.org/pypi/django-custom-user

.. image:: https://img.shields.io/travis/jcugat/django-custom-user/master.svg
    :target: https://travis-ci.org/jcugat/django-custom-user

.. image:: https://img.shields.io/coveralls/jcugat/django-custom-user/master.svg
    :target: https://coveralls.io/r/jcugat/django-custom-user?branch=master

.. image:: https://img.shields.io/pypi/dm/django-custom-user.svg
    :target: https://pypi.python.org/pypi/django-custom-user


Custom user model for Django >= 1.5 with the same behaviour as Django's default User but without a username field. Uses email as the USERNAME_FIELD for authentication.


Quick start
-----------

1. Install django-custom-user with your favorite Python package manager:

.. code-block:: python

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


4. **If you're using Django 1.7+**, you'll have to create migrations for
   ``django-custom-user`` within your working directory:

   1. Create the package directory for the migration module:

      .. code:: sh

          mkdir [project_dir]/custom_user_migrations

   2. Tell Django where the migration package is by adding the following
      setting to ``settings.py``:

      .. code:: python

          MIGRATION_MODULES = {
              'custom_user': '[project_package].custom_user_migrations'
          }

   3. Create the migration:

      .. code:: python

          python manage.py makemigrations custom_user


5. Create the database tables.

.. code-block:: python

    python manage.py syncdb


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


Changelog
---------

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

