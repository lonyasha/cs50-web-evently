from django.utils.timezone import now
from datetime import timedelta
from .models import Event

def delete_old_events():
    threshold_date = now() - timedelta(days=2)
    old_events = Event.objects.filter(date__lt=threshold_date)
    old_events.delete()  # Cascade deletes RSVPs, tasks, and chats

