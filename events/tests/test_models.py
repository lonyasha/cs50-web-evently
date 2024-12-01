import django
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event, RSVP, Task, Chat, ChatParticipant, Message

class ModelsTestCase(TestCase):
    def setUp(self):
        # Create test users and event
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')  # Add user2
        self.event = Event.objects.create(
            title="Test Event",
            date=timezone.now() + timezone.timedelta(days=1),
            description="This is a test event",
            location="Test Location",
            created_by=self.user1
        )

        # Create a Chat for the Event if not already created
        if not hasattr(self.event, 'chat'):
            self.chat = Chat.objects.create(event=self.event)
        else:
            self.chat = self.event.chat

    def test_event_attendees_count(self):
        # Create RSVPs for the event
        RSVP.objects.create(user=self.user1, event=self.event, status='YES')
        RSVP.objects.create(user=self.user2, event=self.event, status='NO')

        # Assert attendees count
        self.assertEqual(self.event.attendees_count(), 1)

    def test_event_status_on_save(self):
        self.event.save()
        self.assertEqual(self.event.status, 'ACTIVE')

    def test_unique_user_event_rsvp_constraint(self):
        # Create a valid RSVP
        RSVP.objects.create(user=self.user1, event=self.event, status='YES')

        # Attempt to create a duplicate RSVP
        with self.assertRaises(Exception):
            RSVP.objects.create(user=self.user1, event=self.event, status='MAYBE')

    def test_chat_is_deletable(self):
        # Ensure the event is set up properly for the test
        self.assertTrue(self.event.date > timezone.now(), "Event date is in the past!")
        
        # Try to create a chat if one does not already exist for this event
        if not Chat.objects.filter(event=self.event).exists():
            chat = Chat.objects.create(event=self.event, created_at=timezone.now() - timezone.timedelta(days=2))
        else:
            chat = Chat.objects.get(event=self.event)
        
        # Ensure only one chat exists for this event
        self.assertEqual(Chat.objects.filter(event=self.event).count(), 1)

        # Test the chat deletion
        chat.delete()
        self.assertFalse(Chat.objects.filter(id=chat.id).exists())

    def test_message_creation(self):
         # Create a message in the existing chat
        message = Message.objects.create(chat=self.chat, user=self.user1, message="Hello, world!")
        self.assertEqual(message.message, "Hello, world!")
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.user, self.user1)

    def test_task_assignment(self):
        # Create a task and assign it
        task = Task.objects.create(event=self.event, assigned_to=self.user1, description="Setup venue")

        # Assert task attributes
        self.assertEqual(task.description, "Setup venue")
        self.assertFalse(task.is_completed)
        self.assertEqual(task.assigned_to, self.user1)

    def test_chat_participant_uniqueness(self):
        # Ensure the creator is already a participant due to the signal
        participant_count = ChatParticipant.objects.filter(chat=self.chat, user=self.user1).count()
        self.assertEqual(
            participant_count,
            1,
            "The event creator should already be a participant in the chat."
        )

        # Attempt to add the same user again and expect a ValueError
        with self.assertRaises(ValueError) as context:
            ChatParticipant.add_participant(chat=self.chat, user=self.user1)

        # Assert that the exception message is correct
        self.assertEqual(
            str(context.exception),
            f"User {self.user1.username} is already a participant of this chat."
        )

        # Confirm that no duplicate entries exist
        self.assertEqual(
            ChatParticipant.objects.filter(chat=self.chat, user=self.user1).count(),
            1,
            "There should still be only one participant entry for the event creator."
        )