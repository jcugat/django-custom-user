# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0001_initial'),
    ]

    operations = [] if django.VERSION < (1, 8) else [
        migrations.AlterField(
            model_name='emailuser',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='email address', db_index=True),
        ),
        migrations.AlterField(
            model_name='emailuser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='emailuser',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
    ]
