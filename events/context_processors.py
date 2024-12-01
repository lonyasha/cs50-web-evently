from .models import RSVP

def maybe_rsvp_count(request):
    if request.user.is_authenticated:
        return {
            'maybe_count': RSVP.objects.filter(user=request.user, status='MAYBE').count()
        }
    return {}
