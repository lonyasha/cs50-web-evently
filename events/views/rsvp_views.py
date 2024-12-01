from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Event, RSVP

@login_required
def rsvp_list(request):
    user_rsvps = RSVP.objects.filter(user=request.user)
    events = Event.objects.filter(pk__in=user_rsvps.values_list('event_id', flat=True),  status='ACTIVE')

    # Count RSVP statuses
    maybe_count = user_rsvps.filter(status='MAYBE').count()

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
        'maybe_count': maybe_count,
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


