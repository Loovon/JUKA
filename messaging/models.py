from django.db import models
from django.conf import settings
from sellers.models import Advert
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages"
    )
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"

    def get_absolute_url(self):
        return f"/messages/conversation/{self.sender.id}/"

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,  # ✅ allow empty for broadcast
    )
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def get_link(self):
        """Return a safe link to the related object, or notifications detail as fallback."""
        if self.content_object:
            try:
                return self.content_object.get_absolute_url()
            except AttributeError:
                return None
        return None

    def __str__(self):
        if self.user:
            return f"Notification for {self.user}: {self.message[:30]}"
        return f"Broadcast: {self.message[:30]}"