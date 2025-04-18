import re
from typing import Any
from notify_lib.constants import MessageType
from notify_lib.models.notifications import SmsNotification
from notify_lib.services.base import NotificationService


class SmsService(NotificationService):
    def __init__(self, vendors):
        self.vendors = vendors
        self.vendor = vendors[0]

    def send(self, notification: SmsNotification) -> str:
        try:
            if notification.message_type == MessageType.OTP.value and not self.vendor.supports_otp():
                raise ValueError(f"Vendor {self.vendor.__class__.__name__} does not support OTP messages")

            msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"
            return self.vendor.send(notification)
        except Exception as e:
            raise

    async def async_send(self, notification: SmsNotification) -> str:
        try:
            if notification.message_type == MessageType.OTP.value and not self.vendor.supports_otp():
                raise ValueError(f"Vendor {self.vendor.__class__.__name__} does not support OTP messages")

            msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"
            return await self.vendor.async_send(notification)
        except Exception as e:
            raise

    def safety_check(self, notification: SmsNotification) -> bool:
        if not notification.items:
            return False

        for item in notification.items:
            if not self._is_valid_phone(item.recipient):
                return False

            if notification.message_type == MessageType.OTP.value and not item.otp:
                return False

        return True

    def get_notification_class(self) -> Any:
        return SmsNotification

    def _is_valid_phone(self, phone: str) -> bool:
        if not phone:
            return False

        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        return len(cleaned) >= 10 and cleaned.isdigit()