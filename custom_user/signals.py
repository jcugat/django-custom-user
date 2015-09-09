import django
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

django_18_migration = '0002_django_18_changes'


def remove_empty_migration_on_django_17(sender, **kwargs):
    if django.VERSION < (1, 8):
        migration_recorder = MigrationRecorder(connection)
        if (sender.name, django_18_migration) in migration_recorder.applied_migrations():
            migration_recorder.record_unapplied(sender.name, django_18_migration)
