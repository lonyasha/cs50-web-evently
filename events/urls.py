from django.urls import path
from .views.auth_views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)
from .views.auth_views import login_view, logout_view, register
from .views.event_task_views import index, event_list, search_users, event_detail, event_form, update_rsvp_list, reload_task_list, create_task, edit_task, toggle_task_completion
from .views.rsvp_views import rsvp_list, rsvp_event
from .views.chat_views import chat_tabs, get_chats, add_message, fetch_latest_messages
from django.conf import settings
from django.urls import include

urlpatterns = [
    path('', index, name='index'),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path('register/', register, name='register'),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('events/', event_list, name='event_list'),
    path('events/<int:pk>/', event_detail, name='event_detail'),
    path('events/<int:pk>/update-rsvp-list/', update_rsvp_list, name='update_rsvp_list'),
    path('events/new/', event_form, name='event_create'),
    path('events/<int:pk>/edit/', event_form, name='event_edit'),
    path('rsvps/', rsvp_list, name='rsvp_list'),
    path('rsvp/<int:pk>/', rsvp_event, name='rsvp_event'),
    path('search-users/', search_users, name='search_users'),
    path('events/<int:pk>/tasks/create/', create_task, name='create_task'),
    path('events/<int:pk>/tasks/reload/', reload_task_list, name='reload_task_list'),
    path('tasks/<int:task_id>/edit/', edit_task, name='edit_task'),
    path('tasks/<int:task_id>/toggle/', toggle_task_completion, name='toggle_task'),
    path('chats/', chat_tabs, name='chat_tabs'),
    path('api/chats/', get_chats, name='get_chats'),
    path('api/chats/<int:chat_id>/messages/add/', add_message, name="add_message"),
    path('api/chats/<int:chat_id>/messages/', fetch_latest_messages, name="fetch_latest_messages"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]