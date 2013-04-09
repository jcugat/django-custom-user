Django Custom User
==================

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

