from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

def get_default_user():
    try:
        return User.objects.get(username='admin').id
    except User.DoesNotExist:
        return None

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
        if self.date and self.date < timezone.now():
            raise ValueError("The event date cannot be in the past.")
        else:
            self.status = 'ACTIVE'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_by', 'date']), # Compound index for created_by and date
        ]
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
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),  # Compound index for user and status
            models.Index(fields=['event', 'status']),  # Compound index for event and status
            models.Index(fields=['event', 'user']),  # Compound index for event and user
            ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'event'], name='unique_user_event_rsvp')
        ]

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
    
    def __str__(self):
        return f"'{self.event.title}' chat"

class ChatParticipant(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["chat", "user"], name="unique_chat_user")
        ]

    @classmethod
    def add_participant(cls, chat, user):
        """
        Adds a participant to a chat. Raises a ValueError if the participant already exists.
        """
        if cls.objects.filter(chat=chat, user=user).exists():
            raise ValueError(f"User {user.username} is already a participant of this chat.")
        return cls.objects.create(chat=chat, user=user)

    def __str__(self):
        return f"{self.user.username} in '{self.chat.event.title}' chat"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)