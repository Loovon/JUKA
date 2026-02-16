from categories.models import Category
from django.http import JsonResponse

def categories_processor(request):
    return {
        "categories": Category.objects.all()
    }

from customers.models import SavedItem

def saved_items(request):
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(SavedItem.objects.filter(user=request.user).values_list("advert_id", flat=True))
    return {'user_saved_ids': saved_ids}

# context_processors.py

from messaging.models import Message, Notification

def unread_counts(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    else:
        unread_messages = 0
        unread_notifications = 0

    return {
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
    }