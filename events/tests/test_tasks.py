from django.test import TestCase
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from unittest.mock import patch
from events.models import Event, Chat, ChatParticipant, RSVP
from events.signals import create_chat_for_event, update_chat_participants  # Add this import
from events.tasks import update_event_status, delete_old_events
from django.db.models.signals import post_save

# Function to disconnect signals for testing
def disconnect_signals():
    post_save.disconnect(create_chat_for_event, sender=Event)
    post_save.disconnect(update_chat_participants, sender=RSVP)

# Function to reconnect signals after the test
def reconnect_signals():
    post_save.connect(create_chat_for_event, sender=Event)
    post_save.connect(update_chat_participants, sender=RSVP)

class TaskFunctionTests(TestCase):
    def setUp(self):
        # Disconnect signals before each test to prevent side effects
        disconnect_signals()

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Mock save method to skip validation for testing purposes
        with patch.object(Event, 'save', lambda instance, *args, **kwargs: super(Event, instance).save(*args, **kwargs)):
            # Create events directly without mocking the save method globally
            self.event_active = Event(
                title="Active Event",
                date=now() + timedelta(days=1),  # Future date
                description="This is an active event.",
                location="Test Location",
                created_by=self.user,
                status="ACTIVE"
            )
            self.event_active.save()  # Save the event to the database

            # Past event that will be marked inactive
            self.event_past = Event(
                title="Past Event",
                date=now() - timedelta(days=1),  # Past date
                description="This is a past event.",
                location="Test Location",
                created_by=self.user,
                status="ACTIVE"
            )
            self.event_past.save()  # Save the event to the database

            # Old event that should be deleted by the delete_old_events function
            self.event_old = Event(
                title="Old Event",
                date=now() - timedelta(days=3),  # Older than threshold for deletion
                description="This is an old event.",
                location="Test Location",
                created_by=self.user,
                status="ACTIVE"
            )
            self.event_old.save()  # Save the event to the database

    def tearDown(self):
        # Reconnect signals after each test
        reconnect_signals()

    def test_update_event_status(self):
        # Call the function to update event statuses
        update_event_status()

        # Reload the events from the database to check for status updates
        self.event_active.refresh_from_db()
        self.event_past.refresh_from_db()

        # Assert that the event is updated to "INACTIVE" if it's past
        self.assertEqual(self.event_active.status, "ACTIVE", "Future event status should remain ACTIVE.")
        self.assertEqual(self.event_past.status, "INACTIVE", "Past event status should be updated to INACTIVE.")

    def test_delete_old_events(self):
        # Ensure the "Old Event" exists before deletion
        old_event_exists = Event.objects.filter(title="Old Event").exists()
        
        self.assertTrue(old_event_exists, "Old event should exist before deletion.")
        
        # Call the function to delete old events
        delete_old_events()

        # Check if the old event is deleted
        old_event_exists_after_deletion = Event.objects.filter(title="Old Event").exists()
        
        # Assert old events are deleted
        self.assertFalse(old_event_exists_after_deletion, "Old event should be deleted.")
        self.assertTrue(Event.objects.filter(title="Active Event").exists(), "Active event should not be deleted.")
        self.assertTrue(Event.objects.filter(title="Past Event").exists(), "Past event should not be deleted.")