import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from ..forms import EventForm
from ..models import Event, RSVP, Task
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import now
from itertools import chain

def index(request):
    '''Display the home page with upcoming events and tasks for the authenticated user. Display a generic page for unauthenticated users.'''
    if request.user.is_authenticated:
        user = request.user

        # Get events where the user is the creator or has RSVP'd "YES"
        upcoming_events = Event.objects.filter(
            Q(created_by=user) | Q(rsvps__user=user, rsvps__status='YES'),
            date__gte=now()
        ).distinct().order_by('date')

        # Get IDs of all upcoming events
        upcoming_events_pks = [event.pk for event in upcoming_events]  

        # Get tasks assigned to the user for events
        tasks = Task.objects.filter(
            assigned_to=user, is_completed=False,
            event__pk__in=upcoming_events_pks
        ).select_related('event')
        
        return render(request, 'events/index.html', {
            'upcoming_events': upcoming_events[:5],
            'tasks': tasks,
        })
    
    return render(request, 'events/index.html')

@login_required
def event_list(request):
    '''Display a list of events that the user is involved in.'''
    user = request.user
    current_time = now()

    events = Event.objects.filter(
        Q(created_by=user) |
        Q(rsvps__user=user, rsvps__status='YES')
    ).distinct()

    # Separate into upcoming and past
    upcoming_events = events.filter(date__gt=current_time).order_by('date')
    past_events = events.filter(date__lte=current_time).order_by('-date')

    return render(request, 'events/event_list.html', {
        'events': {
            'upcoming': upcoming_events,
            'past': past_events,
        }})


@login_required
def event_detail(request, pk):
    '''Display event details and RSVPs to this event.'''
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            user_ids = data.get('user_ids', [])
            if not user_ids:
                return JsonResponse({'message': 'No users provided'}, status=400)
            
            users = User.objects.filter(id__in=user_ids)
            RSVP.objects.bulk_create([
                RSVP(user=user, event=event, status='MAYBE') for user in users
            ])
            return JsonResponse({'message': 'Invitations sent successfully', 'processed_users': user_ids}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=400)
        
    rsvps = event.rsvps.all() 
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_creator': event.created_by == request.user,
        'is_active': event.status == 'ACTIVE',
        'is_attendee': RSVP.objects.filter(event=event, user=request.user, status='YES').exists(),
        'rsvps': rsvps,
        'attendees_count': event.attendees_count(),
        })

@login_required
def event_form(request, pk=None):
    '''Create or edit an event'''
    if pk:
        event = get_object_or_404(Event, pk=pk)
        if event.created_by != request.user:
            messages.error(request, "You do not have permission to edit this event.")
            return redirect('event_detail', pk=pk) 
    else:
        event = None

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            new_event = form.save(commit=False)
            if not pk:  # Set creator only for new events
                new_event.created_by = request.user
            new_event.save()
            return redirect('event_detail', pk=new_event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'event': event})

@login_required
def delete_event(request, pk):
    '''Delete an event'''
    event = get_object_or_404(Event, pk=pk)
    
    if request.user != event.created_by:
        messages.error(request, "You do not have permission to delete this event.")
        return redirect('event_detail', pk=pk)
    
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('event_list')