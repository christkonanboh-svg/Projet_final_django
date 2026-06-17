def create_notification(user, title, message, notification_type, metadata=None):
    from .models import Notification

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        metadata=metadata or {},
    )
