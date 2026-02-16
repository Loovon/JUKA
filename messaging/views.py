# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, Notification
from sellers.models import Advert
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, Max

User = get_user_model()


@login_required
def inbox(request):
    # Fetch all messages where user is involved
    qs = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .select_related("sender", "receiver", "advert")
        .order_by("-timestamp")
    )

    # Group conversations by (other_user, advert)
    conversations = {}
    for msg in qs:

        # Skip if no advert attached (old messages, etc.)
        if not msg.advert:
            continue
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        key = (other_user.id, msg.advert.id)  # 🔑 user + advert unique thread
        if key not in conversations:
            conversations[key] = msg  # keep only latest message

    messages = conversations.values()

    return render(request, "inbox.html", {"messages": messages})


@login_required
def conversation(request, user_id, advert_id):
    other_user = get_object_or_404(User, id=user_id)
    advert = get_object_or_404(Advert, id=advert_id)

    if other_user == request.user:
        return redirect("inbox")

    # Fetch messages for this advert
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
        advert=advert
    ).order_by("timestamp")

    # ✅ Mark all messages from other_user as read for this advert
    unread_qs = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        advert=advert,
        is_read=False
    )
    unread_qs.update(is_read=True)

    # ✅ If sending a new message
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                advert=advert
            )
        return redirect("conversation", user_id=other_user.id, advert_id=advert.id)

    return render(request, "conversation.html", {
        "other_user": other_user,
        "messages": messages,
        "advert": advert
    })

from .models import Notification


# views.py
@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        models.Q(user=request.user) | models.Q(user__isnull=True)
    ).order_by("-timestamp")
    return render(request, "notifications.html", {"notifications": notifications})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)

    # Security: if it's user-specific, make sure it's theirs
    if notif.user and notif.user != request.user:
        return redirect("notifications")  # or raise 403

    if not notif.is_read:
        notif.is_read = True
        notif.save()

    # Redirect if linked object exists
    link = notif.get_link()
    if link:
        return redirect(link)

    # Otherwise go to detail page
    return redirect("notification_detail", notif_id=notif.id)


@login_required
def notification_detail(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)

    # If notification is user-specific, check ownership
    if notif.user and notif.user != request.user:
        return redirect("notifications")  # or raise PermissionDenied

    return render(request, "notification_detail.html", {"notif": notif})


from django.http import JsonResponse


# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, Notification
from sellers.models import Advert
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, Max

User = get_user_model()


@login_required
def inbox(request):
    # Fetch all messages where user is involved
    qs = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .select_related("sender", "receiver", "advert")
        .order_by("-timestamp")
    )

    # Group conversations by (other_user, advert)
    conversations = {}
    for msg in qs:

        # Skip if no advert attached (old messages, etc.)
        if not msg.advert:
            continue
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        key = (other_user.id, msg.advert.id)  # 🔑 user + advert unique thread
        if key not in conversations:
            conversations[key] = msg  # keep only latest message

    messages = conversations.values()

    return render(request, "inbox.html", {"messages": messages})


@login_required
def conversation(request, user_id, advert_id):
    other_user = get_object_or_404(User, id=user_id)
    advert = get_object_or_404(Advert, id=advert_id)

    if other_user == request.user:
        return redirect("inbox")

    # Fetch messages for this advert
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
        advert=advert
    ).order_by("timestamp")

    # ✅ Mark all messages from other_user as read for this advert
    unread_qs = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        advert=advert,
        is_read=False
    )
    unread_qs.update(is_read=True)

    # ✅ If sending a new message
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                advert=advert
            )
        return redirect("conversation", user_id=other_user.id, advert_id=advert.id)

    return render(request, "conversation.html", {
        "other_user": other_user,
        "messages": messages,
        "advert": advert
    })

from .models import Notification


# views.py
@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        models.Q(user=request.user) | models.Q(user__isnull=True)
    ).order_by("-timestamp")
    return render(request, "notifications.html", {"notifications": notifications})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)

    # Security: if it's user-specific, make sure it's theirs
    if notif.user and notif.user != request.user:
        return redirect("notifications")  # or raise 403

    if not notif.is_read:
        notif.is_read = True
        notif.save()

    # Redirect if linked object exists
    link = notif.get_link()
    if link:
        return redirect(link)

    # Otherwise go to detail page
    return redirect("notification_detail", notif_id=notif.id)


@login_required
def notification_detail(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)

    # If notification is user-specific, check ownership
    if notif.user and notif.user != request.user:
        return redirect("notifications")  # or raise PermissionDenied

    return render(request, "notification_detail.html", {"notif": notif})


from django.http import JsonResponse

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, Notification
from sellers.models import Advert
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, Max

User = get_user_model()


@login_required
def inbox(request):

    # Fetch all messages where user is involved
    qs = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .select_related("sender", "receiver", "advert")
        .order_by("-timestamp")
    )

    conversations = {}

    for msg in qs:
        other_user = msg.receiver if msg.sender == request.user else msg.sender

        # Use advert.id OR 0 for advert=None
        advert_key = msg.advert.id if msg.advert else 0

        key = (other_user.id, advert_key)

        if key not in conversations:
            conversations[key] = msg  # latest message per thread

    messages = conversations.values()

    return render(request, "inbox.html", {"messages": messages})


@login_required
def conversation(request, user_id, advert_id):
    other_user = get_object_or_404(User, id=user_id)
    advert = get_object_or_404(Advert, id=advert_id)

    if other_user == request.user:
        return redirect("inbox")

    # Fetch ALL messages between users (advert no longer used)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
    ).order_by("timestamp")

    # Mark all messages from them → you as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    # Sending a new message
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                advert=advert   # keep for future use
            )
        return redirect("conversation", user_id=other_user.id, advert_id=advert.id)

    return render(request, "conversation.html", {
        "other_user": other_user,
        "messages": messages,
        "advert": advert
    })


from .models import Notification


# views.py
@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        models.Q(user=request.user) | models.Q(user__isnull=True)
    ).order_by("-timestamp")
    return render(request, "notifications.html", {"notifications": notifications})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)

    # Security: if it's user-specific, make sure it's theirs
    if notif.user and notif.user != request.user:
        return redirect("notifications")  # or raise 403

    if not notif.is_read:
        notif.is_read = True
        notif.save()

    # Redirect if linked object exists
    link = notif.get_link()
    if link:
        return redirect(link)

    # Otherwise go to detail page
    return redirect("notification_detail", notif_id=notif.id)


@login_required
def notification_detail(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)

    # If notification is user-specific, check ownership
    if notif.user and notif.user != request.user:
        return redirect("notifications")  # or raise PermissionDenied

    return render(request, "notification_detail.html", {"notif": notif})


from django.http import JsonResponse


@login_required
def get_unread_counts(request):
    """
    Return JSON with counts of unread messages (not marked as read)
    and unread notifications for the current logged-in user.
    """
    unread_messages = (
        Message.objects.filter(receiver=request.user, is_read=False).count()
    )

    unread_notifications = (
        Notification.objects.filter(user=request.user, is_read=False).count()
    )

    return JsonResponse({
        "unread_messages": unread_messages,
        "unread_notifications": unread_notifications,
    })



