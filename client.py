from typing import Dict, Any, Optional, List

from constants import MessageType
from factories.pusher_factory import UnifiedPusherFactory
from logger import logger
from models.items import SmsItem
from models.notifications import SmsNotification, EmailNotification
from sender import NotificationSender


class NotificationClient:

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        logger.info("NotificationClient initialized")

    def send_sms(self, notification: SmsNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending {notification.message_type} notification with priority {priority}")

        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {})

        pusher = UnifiedPusherFactory.create_pusher(notification.message_type, config)
        sender = NotificationSender(pusher)
        return sender.process(notification)

    async def async_send_sms(self, notification: SmsNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending {notification.message_type} notification asynchronously with priority {priority}")

        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {})

        pusher = UnifiedPusherFactory.create_pusher(notification.message_type, config)
        sender = NotificationSender(pusher)
        return await sender.async_process(notification)

    def send_transactional_sms(self, phones: List[str], messages: List[str], sender_id: Optional[str] = None,
                               priority: int = 1) -> Dict[str, Any]:
        if len(phones) != len(messages):
            raise ValueError("The number of phone numbers must match the number of messages")

        notification = SmsNotification(sender_id=sender_id, message_type=MessageType.TRANSACTIONAL.value)

        for phone, message in zip(phones, messages):
            notification.add_item(SmsItem(phone, message))

        return self.send_sms(notification, priority)

    def send_promotional_sms(self, phones: List[str], messages: List[str], sender_id: Optional[str] = None,
                             priority: int = 1) -> Dict[str, Any]:
        if len(phones) != len(messages):
            raise ValueError("The number of phone numbers must match the number of messages")

        notification = SmsNotification(sender_id=sender_id, message_type=MessageType.PROMOTIONAL.value)

        for phone, message in zip(phones, messages):
            notification.add_item(SmsItem(phone, message))

        return self.send_sms(notification, priority)

    def send_otp(self, phones: List[str], otps: List[str], messages: Optional[List[str]] = None,
                 sender_id: Optional[str] = None, template_name: Optional[str] = None, priority: int = 1) -> Dict[
        str, Any]:
        if len(phones) != len(otps):
            raise ValueError("The number of phone numbers must match the number of OTP codes")

        if messages and len(phones) != len(messages):
            raise ValueError("The number of messages must match the number of phone numbers")

        notification = SmsNotification(sender_id=sender_id, message_type=MessageType.OTP.value)
        notification.template_name = template_name

        for i, (phone, otp) in enumerate(zip(phones, otps)):
            message = messages[i] if messages else f"Your OTP is {otp}"
            item = SmsItem(phone, message, otp)
            notification.add_item(item)

        return self.send_sms(notification, priority)

    async def async_send_otp(self, phones: List[str], otps: List[str], messages: Optional[List[str]] = None,
                             sender_id: Optional[str] = None, template_name: Optional[str] = None, priority: int = 1) -> \
    Dict[str, Any]:
        if len(phones) != len(otps):
            raise ValueError("The number of phone numbers must match the number of OTP codes")

        if messages and len(phones) != len(messages):
            raise ValueError("The number of messages must match the number of phone numbers")

        notification = SmsNotification(sender_id=sender_id, message_type=MessageType.OTP.value)
        notification.template_name = template_name

        for i, (phone, otp) in enumerate(zip(phones, otps)):
            message = messages[i] if messages else f"Your OTP is {otp}"
            item = SmsItem(phone, message, otp)
            notification.add_item(item)

        return await self.async_send_sms(notification, priority)

    def send_email(self, notification: EmailNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending email notification with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {})

        pusher = UnifiedPusherFactory.create_pusher("email", config)
        sender = NotificationSender(pusher)
        return sender.process(notification)

    async def async_send_email(self, notification: EmailNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending email notification asynchronously with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {})

        pusher = UnifiedPusherFactory.create_pusher("email", config)
        sender = NotificationSender(pusher)
        return await sender.async_process(notification)

