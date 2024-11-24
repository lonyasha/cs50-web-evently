from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, Chat, RSVP, ChatParticipant

@receiver(post_save, sender=Event)
def create_chat_for_event(sender, instance, created, **kwargs):
    if created:
        # Create a chat for the event
        chat = Chat.objects.create(event=instance)
        # Add the event creator as a participant
        ChatParticipant.objects.create(chat=chat, user=instance.creator)

@receiver(post_save, sender=RSVP)
def update_chat_participants(sender, instance, created, **kwargs):
    chat = instance.event.chat
    if instance.status == "yes":
        # Add to chat if RSVP is "yes" and not already a participant
        ChatParticipant.objects.get_or_create(chat=chat, user=instance.user)
    else:
        # Remove participant if their status is no longer "yes"
        ChatParticipant.objects.filter(chat=chat, user=instance.user).delete()
