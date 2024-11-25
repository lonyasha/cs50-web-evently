from django.contrib import admin
from .models import Event, RSVP, Task, Chat, ChatParticipant

admin.site.register(Event)
admin.site.register(RSVP)
admin.site.register(Task)
admin.site.register(Chat)
admin.site.register(ChatParticipant)
