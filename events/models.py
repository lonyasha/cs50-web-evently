from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

def get_default_user():
    return User.objects.get(username='admin').id

class Event(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.TextField()
    location = models.CharField(max_length=255)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events", default=get_default_user)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='ACTIVE')

    def attendees_count(self):
        return self.rsvps.filter(status='YES').count()
    
    def save(self, *args, **kwargs):
        if self.date < timezone.now():
            self.status = 'INACTIVE'
        else:
            self.status = 'ACTIVE'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['date']

class RSVP(models.Model):
    RSVP_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
        ('MAYBE', 'Maybe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rsvps")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    status = models.CharField(max_length=5, choices=RSVP_CHOICES, default='MAYBE')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # Prevent duplicate RSVPs

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
class Task(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.description
    
class Chat(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="chat")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_deletable(self):
        return self.event.date < timezone.now() - timedelta(days=2)

class ChatParticipant(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)