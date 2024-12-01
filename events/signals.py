from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, Chat, RSVP, ChatParticipant

@receiver(post_save, sender=Event)
def create_chat_for_event(sender, instance, created, **kwargs):
    '''Create a chat and chat participant for the event when the event is created.'''
    if created:
        chat, created = Chat.objects.get_or_create(event=instance)
        ChatParticipant.objects.get_or_create(chat=chat, user=instance.created_by)

@receiver(post_save, sender=RSVP)
def update_chat_participants(sender, instance, created, **kwargs):
    '''Update the chat participants when an RSVP is created or updated.'''
    try:
        chat = instance.event.chat  # Retrieve the chat
    except Chat.DoesNotExist:
        return
    
    if instance.status.upper() == "YES":
        ChatParticipant.objects.get_or_create(chat=chat, user=instance.user)
    else:
        ChatParticipant.objects.filter(chat=chat, user=instance.user).delete()