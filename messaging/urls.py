from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name="inbox"),
    path('conversation/<int:user_id>/<int:advert_id>/', views.conversation, name="conversation"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:notif_id>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/<int:notif_id>/", views.notification_detail, name="notification_detail"),
    path("get-unread-counts/", views.get_unread_counts, name="get_unread_counts"),
]
