Django Custom User
==================

.. image:: https://badge.fury.io/py/django-custom-user.png
    :target: http://badge.fury.io/py/django-custom-user

.. image:: https://travis-ci.org/recreatic/django-custom-user.png?branch=master
    :target: https://travis-ci.org/recreatic/django-custom-user

.. image:: https://coveralls.io/repos/recreatic/django-custom-user/badge.png?branch=master
    :target: https://coveralls.io/r/recreatic/django-custom-user?branch=master

.. image:: https://pypip.in/d/django-custom-user/badge.png
    :target: https://crate.io/packages/django-custom-user?version=latest


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


4. Create the database tables.

.. code-block:: python

    python manage.py syncdb


Usage
-----

Instead of referring to ``EmailUser`` directly, you should reference the user model using ``get_user_model()`` as explained in the `Django documentation`_. For example:

.. _Django documentation: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model

.. code-block:: python

    from django.contrib.auth import get_user_model

    user = get_user_model().get(email="user@example.com")


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


Changelog
---------

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

