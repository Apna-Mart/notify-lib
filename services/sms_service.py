import re
from typing import Any

from constants import MessageType
from logger import logger
from models.notifications import SmsNotification
from services.base import NotificationService


class SmsService(NotificationService):
    def __init__(self, vendor):
        self.vendor = vendor

    def send(self, notification: SmsNotification) -> str:
        try:
            if notification.message_type == MessageType.OTP.value and not self.vendor.supports_otp():
                raise ValueError(f"Vendor {self.vendor.__class__.__name__} does not support OTP messages")

            msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"
            logger.info(f"Sending {len(notification.items)} {msg_type} messages")
            return self.vendor.send(notification)
        except Exception as e:
            logger.error(f"Error sending {notification.message_type}: {str(e)}")
            raise

    async def async_send(self, notification: SmsNotification) -> str:
        try:
            if notification.message_type == MessageType.OTP.value and not self.vendor.supports_otp():
                raise ValueError(f"Vendor {self.vendor.__class__.__name__} does not support OTP messages")

            msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"
            logger.info(f"Sending {len(notification.items)} {msg_type} messages asynchronously")
            return await self.vendor.async_send(notification)
        except Exception as e:
            logger.error(f"Error sending {notification.message_type} asynchronously: {str(e)}")
            raise

    def safety_check(self, notification: SmsNotification) -> bool:
        if not notification.items:
            logger.warning("Notification has no items")
            return False

        for item in notification.items:
            if not self._is_valid_phone(item.recipient):
                logger.warning(f"Invalid phone number: {item.recipient}")
                return False

            if notification.message_type == MessageType.OTP.value and not item.otp:
                logger.warning(f"Missing OTP code for recipient: {item.recipient}")
                return False

        return True

    def get_notification_class(self) -> Any:
        return SmsNotification

    def _is_valid_phone(self, phone: str) -> bool:
        if not phone:
            return False

        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        return len(cleaned) >= 10 and cleaned.isdigit()