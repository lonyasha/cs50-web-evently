import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import RegistrationForm, LoginForm, EventForm, TaskForm
from .models import Event, RSVP, Task, Chat, Message, ChatParticipant
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.timezone import now


def index(request):
    return render(request, 'events/index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect("index")
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, "registration/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    return redirect("index")

def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registration successful! You are now logged in.')
        return redirect("index")

    return render(request, 'registration/register.html', {'form': form})

@login_required
def event_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/event_list.html', {'events': events})

@csrf_exempt
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).values('id', 'username', 'first_name', 'last_name')
        
        return JsonResponse(list(users), safe=False)
    return JsonResponse([], safe=False)

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_creator = event.created_by == request.user

    # if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
    #     try:
    #         data = json.loads(request.body)
           
    #         usernames = data.get('usernames', [])

    #         if not usernames:
    #                 return JsonResponse({"error": "No usernames provided."}, status=400)

    #         users_to_invite = []

    #         for username in usernames:
    #             user = User.objects.filter(username=username).first()
    #             if user:
    #                 users_to_invite.append(user)

            
    #         for user in users_to_invite:
    #             try:
    #                 if not RSVP.objects.filter(event=event, user=user).exists():
    #                     RSVP.objects.create(event=event, user=user, status='MAYBE')
    #             except Exception as e:
    #                 print(f"Error creating RSVP for {user.username}: {e}")

    #         response = {"message": f"Invitations sent to {', '.join(usernames)}"}
    #         return JsonResponse(response)
    #     except Exception as e:
    #         return JsonResponse({"error": str(e)}, status=500)

    rsvps = event.rsvps.all() 
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_creator': is_creator,
        'rsvps': rsvps,
        'attendees_count': event.attendees_count(),
        })

@login_required
def event_form(request, pk=None):
    if pk:
        event = get_object_or_404(Event, pk=pk)
        if event.created_by != request.user:
            return redirect('event_list')  # Prevent editing if not the creator
    else:
        event = None

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            new_event = form.save(commit=False)
            if not pk:  # Set creator only for new events
                new_event.created_by = request.user
            new_event.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'event': event})

@login_required
def rsvp_list(request):
    user_rsvps = RSVP.objects.filter(user=request.user)
    events = Event.objects.filter(pk__in=user_rsvps.values_list('event_id', flat=True),  status='ACTIVE')

    # Create a dictionary mapping event IDs to the user's RSVP status
    rsvp_status = {rsvp.event.pk: rsvp.status for rsvp in user_rsvps}

    event_rsvp_status = []
    for event in events:
        event_rsvp_status.append({
            'event': event,
            'status': rsvp_status.get(event.pk)
        })

    return render(request, 'events/rsvp_list.html', {
        'event_rsvp_status': event_rsvp_status,
    })

@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.status == 'INACTIVE':
        messages.error(request, f"Sorry, the event '{event.title}' has already happened.")
        return redirect('rsvp_list')

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['YES', 'NO', 'MAYBE']:
            rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
            rsvp.status = status
            rsvp.save()
            messages.success(request, f'RSVP for "{event.title}" updated to "{status}".')
        else:
            messages.error(request, "Invalid RSVP status.")

    return redirect('rsvp_list')

@login_required
def load_task_form(request, pk=None, task_id=None):
    if task_id:
        task = get_object_or_404(Task, id=task_id)
        form = TaskForm(instance=task)
    else:
        event = get_object_or_404(Event, pk=pk)
        form = TaskForm(event=event)

    html = render_to_string('events/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def create_task(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, event=event)
        if form.is_valid():
            task = form.save(commit=False)
            task.event = event
            task.save()
            return JsonResponse({'success': True})

        html = render_to_string('events/task_form_partial.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'html': html})

    form = TaskForm(event=event)
    html = render_to_string('events/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})

        html = render_to_string('events/task_form_partial.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'html': html})

    form = TaskForm(instance=task)
    html = render_to_string('events/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

def toggle_task_completion(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('event_detail', pk=task.event.pk)

@login_required
def chat_list(request):
    user = request.user
    chats = ChatParticipant.objects.filter(user=user).select_related('chat', 'chat__event')

    # Fetch chat data for rendering
    chat_data = []
    for participant in chats:
        chat = participant.chat
        warning = None
        if chat.event.due_date < now():
            warning = "This chat will be deleted in 2 days."
        chat_data.append({
            'id': chat.id,
            'name': chat.event.name,
            "warning": warning,
            'messages': [
                {'user': msg.user.username, 'message': msg.message, 'created_at': msg.created_at}
                for msg in chat.messages.order_by('created_at')
            ],
        })

    # Render the template
    return render(request, "events/chat_list.html", {"chats": chat_data})

@login_required
def get_chat(request, pk):
    user = request.user
    chats = ChatParticipant.objects.filter(user=user).select_related('chat', 'chat__event')
    chat_data = []

    for participant in chats:
        chat = participant.chat
        warning = None
        if chat.event.date < now():
            warning = "This chat will be deleted in 2 days."
        chat_data.append({
            'id': chat.id,
            'name': chat.event.name,
            "warning": warning,
            'messages': [
                {'user': msg.user.username, 'message': msg.message, 'created_at': msg.created_at}
                for msg in chat.messages.order_by('created_at')
            ],
        })
    return JsonResponse(chat_data, safe=False)

@login_required
def add_message(request, chat_id):
    if request.method == "POST":
        user = request.user
        chat = get_object_or_404(Chat, id=chat_id)

        # Ensure the user is a participant
        if not ChatParticipant.objects.filter(chat=chat, user=user).exists():
            return JsonResponse({"status": "error", "message": "You are not a participant in this chat."}, status=403)

        # Add the message
        data = json.loads(request.body)
        message_text = data.get("message")
        if message_text:
            Message.objects.create(chat=chat, user=user, message=message_text)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

def fetch_latest_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('created_at')
    warning = None
    if chat.event.due_date < now():
        warning = "This chat will be deleted in 2 days."

    return JsonResponse({
        'warning': warning,
        'messages': [
            {'user': msg.user.username, 'message': msg.message, 'created_at': msg.created_at}
            for msg in messages
        ]
    })