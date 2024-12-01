import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import Chat, Message, ChatParticipant
from django.utils.timezone import now

def fetch_chat_data(user):
    """Fetch and prepare chat data for a given user."""
    chats = ChatParticipant.objects.filter(user=user).select_related('chat', 'chat__event')
    chat_data = []

    for participant in chats:
        chat = participant.chat
        warning = None

        if chat.event.date < now():  
            warning = "This chat will be deleted soon."

        chat_data.append({
            'id': chat.id,
            'name': chat.event.title,
            'event_pk': chat.event.pk,
            'warning': warning,
            'messages': [
                {'user': msg.user.username, 'message': msg.message, 'created_at': msg.created_at}
                for msg in chat.messages.order_by('created_at')
            ],
        })
    return chat_data

@login_required
def chat_tabs(request):
    """Render the chat tabs with the user’s chat data."""
    user = request.user
    chat_data = fetch_chat_data(user)
    # Render the template
    return render(request, "events/chat_tabs.html", {"chats": chat_data})

@login_required
def get_chats(request):
    """Return chat data for the user as JSON."""
    user = request.user
    chat_data = fetch_chat_data(user)
    return JsonResponse(chat_data, safe=False)

@login_required
def add_message(request, chat_id):
    """Add a message to a specific chat."""
    if request.method == "POST":
        user = request.user
        chat = get_object_or_404(Chat, id=chat_id)

        # Add the message
        data = json.loads(request.body)
        message_text = data.get("message")
        if message_text:
            Message.objects.create(chat=chat, user=user, message=message_text)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def fetch_latest_messages(request, chat_id):
    """Fetch the latest messages for a specific chat."""
    chat = get_object_or_404(Chat, id=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('created_at')
    warning = None
    if chat.event.date < now():
        warning = "This chat will be deleted soon."

    return JsonResponse({
        'warning': warning,
        'messages': [
            {'user': msg.user.username, 'message': msg.message, 'created_at': msg.created_at}
            for msg in messages
        ]
    })