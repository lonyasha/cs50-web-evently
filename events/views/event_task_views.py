import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.template.loader import render_to_string
from ..forms import EventForm, TaskForm
from ..models import Event, RSVP, Task
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.timezone import now
from itertools import chain

def index(request):
    if request.user.is_authenticated:
        user = request.user

         # Get events where the user is the creator
        created_events = Event.objects.filter(
            created_by=user, date__gte=now()
        ).order_by('date')

        # Get events where the user has RSVP'd "YES"
        rsvp_events = Event.objects.filter(
            rsvps__user=user, rsvps__status='YES', date__gte=now()
        ).order_by('date')

        # Combine the two querysets and get the first 5 events
        upcoming_events = list(chain(created_events, rsvp_events))[:5]

        # Get tasks assigned to the user for events
        tasks = Task.objects.filter(
            assigned_to=user, is_completed=False
        ).select_related('event')
        
        return render(request, 'events/index.html', {
            'upcoming_events': upcoming_events,
            'tasks': tasks,
        })
    
    return render(request, 'events/index.html')

@login_required
def event_list(request):
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
def update_rsvp_list(request, pk):
    event = get_object_or_404(Event, pk=pk)
    rsvps = event.rsvps.all()
    html = render_to_string('includes/rsvp_list_partial.html', {'rsvps': rsvps}, request=request)
    return JsonResponse({'html': html})

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
def load_task_form(request, pk=None, task_id=None):
    if task_id:
        task = get_object_or_404(Task, id=task_id)
        form = TaskForm(instance=task)
    else:
        event = get_object_or_404(Event, pk=pk)
        form = TaskForm(event=event)

    html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def reload_task_list(request, pk):
    event = get_object_or_404(Event, pk=pk)
    tasks = event.task_set.all().order_by('-id') 
    
    html = render_to_string('includes/task_list_partial.html', {'tasks': tasks, 'event': event}, request=request)
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
        else:
            html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'html': html})

    form = TaskForm(event=event)
    html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'html': html})

    form = TaskForm(instance=task)
    html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def toggle_task_completion(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.is_completed = not task.is_completed
    task.save()
    
    # Redirect to the referring page
    referer = request.META.get('HTTP_REFERER')  # Get the referring URL
    if referer:
        return redirect(referer)  # Redirect back to where the request came from
    
    # Fallback: Default to event detail if no referer is found
    return redirect('event_detail', pk=task.event.pk)