from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from events.forms import (
    RegistrationForm,
    LoginForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    EventForm,
    RSVPForm,
    TaskForm,
)
from events.models import Event, RSVP

class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )
        future_date = now() + timedelta(days=1)
        self.event = Event.objects.create(
            title="Test Event",
            date=future_date,
            location="Test Location",
            description="Test Description",
            created_by=self.user,
        )

    def test_registration_form(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_registration_form_email_unique(self):
        data = {
            "username": "anotheruser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "password123",
            "password2": "password123",
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_login_form(self):
        data = {"username": "testuser", "password": "password123"}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_password_reset_form(self):
        data = {"email": "test@example.com"}
        form = CustomPasswordResetForm(data=data)
        self.assertTrue(form.is_valid())

    def test_set_password_form(self):
        form = CustomSetPasswordForm(
            user=self.user,
            data={
                "new_password1": "newpassword123",
                "new_password2": "newpassword123",
            },
        )
        self.assertTrue(form.is_valid())

    def test_event_form(self):
        data = {
            "title": "Updated Event",
            "date": now(),
            "location": "New Location",
            "description": "Updated Description",
        }
        form = EventForm(data=data)
        self.assertTrue(form.is_valid())

    def test_rsvp_form(self):
        data = {"status": "YES"}
        form = RSVPForm(data=data)
        self.assertTrue(form.is_valid())

    def test_task_form_valid(self):
        rsvp_yes_user = User.objects.create_user(username="rsvpuser", password="password")
        RSVP.objects.create(event=self.event, user=rsvp_yes_user, status="YES")
        data = {
            "assigned_to": rsvp_yes_user.id,
            "description": "Complete the task",
            "is_completed": False,
        }
        form = TaskForm(event=self.event, data=data)
        self.assertTrue(form.is_valid())

    def test_task_form_invalid_user(self):
        other_user = User.objects.create_user(username="otheruser", password="password")
        data = {
            "assigned_to": other_user.id,
            "description": "Invalid user task",
            "is_completed": False,
        }
        form = TaskForm(event=self.event, data=data)
        self.assertFalse(form.is_valid())