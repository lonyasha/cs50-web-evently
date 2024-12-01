from django.test import TestCase
from django.urls import reverse, resolve
from events.views.auth_views import login_view, logout_view, register
from events.views.event_views import index, event_list, event_detail, event_form
from events.views.rsvp_views import rsvp_list, rsvp_event, update_rsvp_list
from events.views.chat_views import chat_tabs, get_chats, add_message, fetch_latest_messages
from events.views.task_views import create_task, reload_task_list, edit_task, toggle_task_completion
from events.views.auth_views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

class TestUrls(TestCase):

    def test_index_url(self):
        url = reverse('index')
        view = resolve(url)
        self.assertEqual(view.func, index)

    def test_login_url(self):
        url = reverse('login')
        view = resolve(url)
        self.assertEqual(view.func, login_view)

    def test_logout_url(self):
        url = reverse('logout')
        view = resolve(url)
        self.assertEqual(view.func, logout_view)

    def test_register_url(self):
        url = reverse('register')
        view = resolve(url)
        self.assertEqual(view.func, register)

    def test_password_reset_urls(self):
        url = reverse('password_reset')
        view = resolve(url)
        self.assertEqual(view.func.view_class, CustomPasswordResetView)
        
        url = reverse('password_reset_done')
        view = resolve(url)
        self.assertEqual(view.func.view_class, CustomPasswordResetDoneView)

        url = reverse('password_reset_confirm', kwargs={'uidb64': 'dummy', 'token': 'dummy'})
        view = resolve(url)
        self.assertEqual(view.func.view_class, CustomPasswordResetConfirmView)
        
        url = reverse('password_reset_complete')
        view = resolve(url)
        self.assertEqual(view.func.view_class, CustomPasswordResetCompleteView)

    def test_event_list_url(self):
        url = reverse('event_list')
        view = resolve(url)
        self.assertEqual(view.func, event_list)

    def test_event_detail_url(self):
        url = reverse('event_detail', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEqual(view.func, event_detail)

    def test_event_create_url(self):
        url = reverse('event_create')
        view = resolve(url)
        self.assertEqual(view.func, event_form)

    def test_event_edit_url(self):
        url = reverse('event_edit', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEqual(view.func, event_form)

    def test_rsvp_list_url(self):
        url = reverse('rsvp_list')
        view = resolve(url)
        self.assertEqual(view.func, rsvp_list)

    def test_rsvp_event_url(self):
        url = reverse('rsvp_event', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEqual(view.func, rsvp_event)

    def test_chat_tabs_url(self):
        url = reverse('chat_tabs')
        view = resolve(url)
        self.assertEqual(view.func, chat_tabs)

    def test_get_chats_url(self):
        url = reverse('get_chats')
        view = resolve(url)
        self.assertEqual(view.func, get_chats)

    def test_add_message_url(self):
        url = reverse('add_message', kwargs={'chat_id': 1})
        view = resolve(url)
        self.assertEqual(view.func, add_message)

    def test_fetch_latest_messages_url(self):
        url = reverse('fetch_latest_messages', kwargs={'chat_id': 1})
        view = resolve(url)
        self.assertEqual(view.func, fetch_latest_messages)

    def test_update_rsvp_list_url(self):
        url = reverse('update_rsvp_list', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEqual(view.func, update_rsvp_list)

    def test_reload_task_list_url(self):
        url = reverse('reload_task_list', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEqual(view.func, reload_task_list)

    def test_create_task_url(self):
        url = reverse('create_task', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEqual(view.func, create_task)

    def test_edit_task_url(self):
        url = reverse('edit_task', kwargs={'task_id': 1})
        view = resolve(url)
        self.assertEqual(view.func, edit_task)

    def test_toggle_task_url(self):
        url = reverse('toggle_task', kwargs={'task_id': 1})
        view = resolve(url)
        self.assertEqual(view.func, toggle_task_completion)

