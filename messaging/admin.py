from django.contrib import admin
from .models import Message, Conversation, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "advert", "content", "timestamp", "is_read")
    list_filter = ("is_read", "timestamp")
    search_fields = ("content", "sender__username", "receiver__username")

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    filter_horizontal = ("participants",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "link", "is_read", "timestamp")
    list_filter = ("is_read", "timestamp")
    search_fields = ("message", "user__username")
