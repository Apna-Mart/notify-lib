"""SMS notification pusher."""

import re
from typing import Any

from logger import logger
from models.notifications import SmsNotification
from pushers.base import NotificationPusher


class SmsPusher(NotificationPusher):

    def __init__(self, vendor):
        self.vendor = vendor

    def send(self, notification: SmsNotification) -> str:
        try:
            logger.info(f"Sending {len(notification.items)} SMS messages")
            return self.vendor.send(notification)
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise

    async def async_send(self, notification: SmsNotification) -> str:
        try:
            logger.info(f"Sending {len(notification.items)} SMS messages asynchronously")
            return await self.vendor.async_send(notification)
        except Exception as e:
            logger.error(f"Error sending SMS asynchronously: {str(e)}")
            raise

    def safety_check(self, notification: SmsNotification) -> bool:
        if not notification.items:
            logger.warning("SMS notification has no items")
            return False

        for item in notification.items:
            if not self._is_valid_phone(item.recipient):
                logger.warning(f"Invalid phone number: {item.recipient}")
                return False

        return True

    def get_notification_class(self) -> Any:
        return SmsNotification

    def _is_valid_phone(self, phone: str) -> bool:
        if not phone:
            return False

        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        return len(cleaned) >= 10 and cleaned.isdigit()