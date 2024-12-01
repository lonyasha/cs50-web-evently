from django.urls import path
from .views.auth_views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)
from .views.auth_views import login_view, logout_view, register
from .views.event_views import index, event_list, event_detail, event_form, delete_event
from .views.rsvp_views import search_users, update_rsvp_list, rsvp_list, rsvp_event
from .views.task_views import create_task, reload_task_list, edit_task, toggle_task_completion, delete_task
from .views.chat_views import chat_tabs, get_chats, add_message, fetch_latest_messages
from django.conf import settings
from django.urls import include

urlpatterns = [
    # index(event) view 
    path('', index, name='index'),
    # auth views
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path('register/', register, name='register'),
    # password reset views
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # event views
    path('events/', event_list, name='event_list'),
    path('events/<int:pk>/', event_detail, name='event_detail'),
    path('events/new/', event_form, name='event_create'),
    path('events/<int:pk>/edit/', event_form, name='event_edit'),
    path('event/<int:pk>/delete/', delete_event, name='event_delete'),
    # rsvp views
    path('search-users/', search_users, name='search_users'),
    path('events/<int:pk>/update-rsvp-list/', update_rsvp_list, name='update_rsvp_list'),
    path('rsvps/', rsvp_list, name='rsvp_list'),
    path('rsvp/<int:pk>/', rsvp_event, name='rsvp_event'),
    # task views
    path('events/<int:pk>/tasks/create/', create_task, name='create_task'),
    path('events/<int:pk>/tasks/reload/', reload_task_list, name='reload_task_list'),
    path('tasks/<int:task_id>/edit/', edit_task, name='edit_task'),
    path('tasks/<int:task_id>/toggle/', toggle_task_completion, name='toggle_task'),
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),
    # chat views
    path('chats/', chat_tabs, name='chat_tabs'),
    path('api/chats/', get_chats, name='get_chats'),
    path('api/chats/<int:chat_id>/messages/add/', add_message, name="add_message"),
    path('api/chats/<int:chat_id>/messages/', fetch_latest_messages, name="fetch_latest_messages"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]