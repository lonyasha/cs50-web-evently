from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/new/', views.event_form, name='event_create'),
    path('events/<int:pk>/edit/', views.event_form, name='event_edit'),
    path('rsvps/', views.rsvp_list, name='rsvp_list'),
    path('rsvp/<int:pk>/', views.rsvp_event, name='rsvp_event'),
    path('search-users/', views.search_users, name='search_users'),
    path('events/<int:pk>/tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/toggle/', views.toggle_task_completion, name='toggle_task'),
     path('chats/', views.chat_list, name='chat_list'),
    path('api/events/<int:pk>/chats/', views.get_chat, name='get_chat'),
    path('api/chats/<int:chat_id>/messages/add/', views.add_message, name="add_message"),
    path('api/chats/<int:chat_id>/messages/', views.fetch_latest_messages, name="fetch_latest_messages"),
]
