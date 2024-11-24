from django.contrib import admin
from .models import Event, RSVP, Task

admin.site.register(Event)
admin.site.register(RSVP)
admin.site.register(Task)
