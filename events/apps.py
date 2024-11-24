from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError, ProgrammingError


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        import events.signals  # Import the signals to connect them
        from django_q.tasks import schedule, Schedule
        
        try:
            from django_q.tasks import schedule, Schedule
            # Only schedule the task if the table exists
            if not Schedule.objects.filter(func='events.tasks.delete_old_events').exists():
                schedule(
            'events.tasks.delete_old_events',
            schedule_type='D',
                )
        except (OperationalError, ProgrammingError, ImproperlyConfigured):
            # Skip if the database is not ready (e.g., during migrations)
            pass
