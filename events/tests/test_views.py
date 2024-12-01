from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Event, Task, RSVP, Chat, ChatParticipant, Message
from django.utils.timezone import now, timedelta
from django.db.models.signals import post_save
from events.signals import create_chat_for_event, update_chat_participants
from unittest.mock import patch
from django.http import JsonResponse

class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Disconnect signals before running tests.'''
        super().setUpClass()
        # Disconnect signals
        post_save.disconnect(create_chat_for_event, sender=Event)
        post_save.disconnect(update_chat_participants, sender=RSVP)

    @classmethod
    def tearDownClass(cls):
        '''Reconnect signals after running tests.'''
        # Reconnect signals after tests
        post_save.connect(create_chat_for_event, sender=Event)
        post_save.connect(update_chat_participants, sender=RSVP)
        super().tearDownClass()

    def setUp(self):
        '''Create users, an event, and a chat for testing.'''
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        # Log in the first user
        self.client.login(username="user1", password="password123")

        # Create an event
        self.event = Event.objects.create(
            title="Test Event",
            date=now() + timedelta(days=1),
            description="This is a test event.",
            location="Test Location",
            created_by=self.user1,
            status="ACTIVE"
        )

        # Ensure no duplicate chats are created
        try:
            self.chat = Chat.objects.get(event=self.event)
        except Chat.DoesNotExist:
            self.chat = Chat.objects.create(event=self.event)

        # Add participants
        ChatParticipant.objects.get_or_create(chat=self.chat, user=self.user1)

        self.task = Task.objects.create(
            event=self.event,
            description="Task for testing",
            assigned_to=self.user2,
            is_completed=False
        )

    def test_login_view(self):
        '''Test that the login view works correctly.'''
        response = self.client.post(reverse('login'), {'username': 'user1', 'password': 'password123'})
        self.assertRedirects(response, reverse('index'))

    def test_logout_view(self):
        '''Test that the logout view'''
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)  # Redirect after logout

    def test_register_view(self):
        '''Test that the register view works correctly.'''
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertRedirects(response, reverse('index'))

    def test_event_list_view(self):
        '''Test that the event_list view works correctly.'''
        response = self.client.get(reverse("event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_event_detail_view(self):
        '''Test that the event_detail view works correctly.'''
        response = self.client.get(reverse("event_detail", args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_rsvp_event(self):
        '''Test that the rsvp_event view works correctly.'''
        response = self.client.post(reverse("rsvp_event", args=[self.event.pk]), {"status": "YES"})
        self.assertEqual(response.status_code, 302)  # Redirect to RSVP list
        self.assertTrue(RSVP.objects.filter(user=self.user1, event=self.event, status="YES").exists())

    @patch("django.core.handlers.base.BaseHandler.get_response")
    def test_chat_tabs_view(self, mock_fetch):
        '''Test that the chat_tabs view works correctly.'''
        # Mock the fetch response to return chat data
        mock_response = JsonResponse({
            "chats": [
                {
                    "id": self.chat.id,
                    "event_pk": self.chat.event.pk,
                    "name": str(self.chat),  # Use the Chat's string representation
                    "messages": [],
                }
            ]
        })
        mock_fetch.return_value = mock_response

        response = self.client.get(reverse("chat_tabs"))
        self.assertContains(response, "Test Event")

    def test_add_message_to_chat(self):
        '''Test that the add_message view works correctly.'''
        response = self.client.post(reverse("add_message", args=[self.chat.pk]), {
            "message": "Test Message"
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Message.objects.filter(chat=self.chat, user=self.user1, message="Test Message").exists())

    def test_toggle_task_completion(self):
        response = self.client.post(reverse("toggle_task", args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

    def test_delete_event(self):
        """Test that the delete_event view works correctly."""
        # Ensure the event exists
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())

        # Call delete_event
        response = self.client.post(reverse("event_delete", args=[self.event.pk]))
        
        # Assert the event is deleted
        self.assertRedirects(response, reverse("event_list"))
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_delete_task(self):
        """Test that the delete_task view works correctly."""
        # Ensure the task exists
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

        # Call delete_task
        response = self.client.post(reverse("delete_task", args=[self.task.id]))
        
        # Assert the task is deleted
        self.assertRedirects(response, reverse("event_detail", args=[self.event.pk]))
        self.assertFalse(Task.objects.filter(pk=self.task.id).exists())