"""OTP notification pusher."""

import re
from typing import Any

from logger import logger
from models.notifications import OtpNotification
from pushers.base import NotificationPusher


class OtpPusher(NotificationPusher):
    def __init__(self, vendor):
        self.vendor = vendor

    def send(self, notification: OtpNotification) -> str:
        try:
            logger.info(f"Sending {len(notification.items)} OTP messages")
            return self.vendor.send(notification)
        except Exception as e:
            logger.error(f"Error sending OTP: {str(e)}")
            raise

    async def async_send(self, notification: OtpNotification) -> str:
        try:
            logger.info(f"Sending {len(notification.items)} OTP messages asynchronously")
            return await self.vendor.async_send(notification)
        except Exception as e:
            logger.error(f"Error sending OTP asynchronously: {str(e)}")
            raise

    def safety_check(self, notification: OtpNotification) -> bool:
        if not notification.items:
            logger.warning("OTP notification has no items")
            return False

        for item in notification.items:
            if not self._is_valid_phone(item.recipient):
                logger.warning(f"Invalid phone number: {item.recipient}")
                return False

            if not hasattr(item, 'otp') or not item.otp:
                logger.warning(f"Missing OTP for recipient: {item.recipient}")
                return False

        return True

    def get_notification_class(self) -> Any:
        return OtpNotification

    def _is_valid_phone(self, phone: str) -> bool:
        if not phone:
            return False

        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        return len(cleaned) >= 10 and cleaned.isdigit()