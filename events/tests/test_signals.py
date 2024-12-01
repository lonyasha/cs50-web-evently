from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from django.db import connection
from unittest.mock import patch
from django.db.models.signals import post_save
from events.models import Event, RSVP, Chat, ChatParticipant
from events.signals import update_chat_participants


class SignalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable foreign key constraints for SQLite
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_keys = ON;')
            result = cursor.execute('PRAGMA foreign_keys;').fetchone()
            print(f"Foreign key enforcement during tests: {result[0]}")  # Should print "1"

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create a test event
        self.event = Event.objects.create(
            title="Test Event",
            date=now() + timedelta(days=1),
            created_by=self.user,
        )

        # Create a chat for the event (if not already created by the signal)
        self.chat, _ = Chat.objects.get_or_create(event=self.event)

    @patch('events.signals.create_chat_for_event')
    def test_create_chat_for_event_signal(self, mock_create_chat):
        # Trigger any necessary actions to fire the signal
        self.event.save()

        # Ensure that no extra Chat objects were created by the signal
        self.assertFalse(Chat.objects.filter(event=self.event).count() > 1)

    def test_no_error_when_chat_missing(self):
        # Disconnect the signal
        post_save.disconnect(update_chat_participants, sender=RSVP)

        # Store the chat ID
        chat_id = self.chat.id

        # Delete the chat
        self.chat.delete()

        # Ensure no ChatParticipant exists for the deleted chat
        self.assertFalse(ChatParticipant.objects.filter(chat_id=chat_id).exists())

        # User RSVPs "YES" after chat deletion
        RSVP.objects.create(user=self.user, event=self.event, status="YES")

        # Verify that no ChatParticipant is created since the chat is missing
        self.assertFalse(ChatParticipant.objects.filter(user=self.user).exists())

        # Reconnect the signal
        post_save.connect(update_chat_participants, sender=RSVP)

    def test_chat_and_participant_creation_on_event_creation(self):
        event = Event.objects.create(
            title="Test Event",
            date=now() + timedelta(days=1),  # Ensure valid date
            created_by=self.user  # Ensure user is saved
        )
        chat = Chat.objects.get(event=event)
        self.assertIsNotNone(chat, "Chat should be created for the event")

        participant = ChatParticipant.objects.get(chat=chat, user=self.user)
        self.assertIsNotNone(participant, "ChatParticipant should be added for the event creator")

    def test_add_chat_participant_on_rsvp_yes(self):
        # User RSVPs "YES"
        RSVP.objects.create(user=self.user, event=self.event, status="YES")

        # Verify that the ChatParticipant was created
        self.assertTrue(
            ChatParticipant.objects.filter(chat=self.chat, user=self.user).exists()
        )

    def test_remove_chat_participant_on_rsvp_change(self):
        # User RSVPs "YES"
        rsvp = RSVP.objects.create(user=self.user, event=self.event, status="YES")
        self.assertTrue(
            ChatParticipant.objects.filter(chat=self.chat, user=self.user).exists(),
            "ChatParticipant should be created when RSVP is YES"
        )

        # Change RSVP status to "NO"
        rsvp.status = "NO"
        rsvp.save()

        # Verify that the ChatParticipant was removed
        self.assertFalse(
            ChatParticipant.objects.filter(chat=self.chat, user=self.user).exists(),
            "ChatParticipant should be removed when RSVP is changed to NO"
        )

    def test_no_chat_participant_created_for_rsvp_no(self):
        # User RSVPs "NO"
        RSVP.objects.create(user=self.user, event=self.event, status="NO")

        # Verify that no ChatParticipant was created
        self.assertFalse(
            ChatParticipant.objects.filter(chat=self.chat, user=self.user).exists(),
            "ChatParticipant should be removed when RSVP is changed to NO"
        )

    def test_chat_participant_cleanup_on_chat_delete(self):
        # Create RSVP to add a ChatParticipant
        RSVP.objects.create(user=self.user, event=self.event, status="YES")

        # Verify ChatParticipant exists
        self.assertTrue(
            ChatParticipant.objects.filter(chat=self.chat, user=self.user).exists(),
            "ChatParticipant should exist after RSVP with status 'YES'"
        )

        # Delete the chat
        self.chat.delete()

        # Verify ChatParticipant is cleaned up
        self.assertFalse(
            ChatParticipant.objects.filter(user=self.user).exists(),
            "ChatParticipant should be deleted when the associated Chat is deleted"
        )