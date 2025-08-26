import re
from typing import Any
from notify_lib.models.notifications import EmailNotification
from notify_lib.services.base import NotificationService


class EmailService(NotificationService):
    def __init__(self, vendors):
        self.vendors = vendors
        self.vendor = vendors[0]

    def send(self, notification: EmailNotification) -> str:
        try:
            return self.vendor.send(notification)
        except Exception as e:
            raise

    async def async_send(self, notification: EmailNotification) -> str:
        try:
            return await self.vendor.async_send(notification)
        except Exception as e:
            raise

    def safety_check(self, notification: EmailNotification) -> bool:
        if not notification.items:
            return False
        if not self._is_valid_email(notification.from_email):
            return False
        if not notification.subject:
            return False
        for item in notification.items:
            if not self._is_valid_email(item.recipient):
                return False
        return True

    def get_notification_class(self) -> Any:
        return EmailNotification

    def _is_valid_email(self, email: str) -> bool:
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))