from django.utils.timezone import now
from datetime import timedelta
from .models import Event

def update_event_status():
    """Update the status of events from 'active' to 'inactive' if the event date has passed."""
    # Query all active events where the event date has passed
    events_to_update = Event.objects.filter(status='ACTIVE', date__lte=now())
    events_to_update.update(status='INACTIVE')  # Bulk update the status

def delete_old_events():
    threshold_date = now() - timedelta(days=2)
    old_events = Event.objects.filter(date__lt=threshold_date)
    old_events.delete()  # Cascade deletes RSVPs, tasks, and chats associated with the event