from typing import Dict, Any, Optional

from factories.pusher_factory import PusherFactory
from logger import logger
from models.notifications import SmsNotification, EmailNotification, OtpNotification
from sender import NotificationSender


class NotificationClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        logger.info("NotificationClient initialized")

    def send_sms(self, notification: SmsNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending SMS notification with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {}).get("sms", {})

        pusher = PusherFactory.create_pusher("sms", config)
        sender = NotificationSender(pusher)
        return sender.process(notification)

    async def async_send_sms(self, notification: SmsNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending SMS notification asynchronously with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {}).get("sms", {})

        pusher = PusherFactory.create_pusher("sms", config)
        sender = NotificationSender(pusher)
        return await sender.async_process(notification)

    def send_email(self, notification: EmailNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending email notification with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {}).get("email", {})

        pusher = PusherFactory.create_pusher("email", config)
        sender = NotificationSender(pusher)
        return sender.process(notification)

    async def async_send_email(self, notification: EmailNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending email notification asynchronously with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {}).get("email", {})

        pusher = PusherFactory.create_pusher("email", config)
        sender = NotificationSender(pusher)
        return await sender.async_process(notification)

    def send_otp(self, notification: OtpNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending OTP notification with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {}).get("otp", {})

        pusher = PusherFactory.create_pusher("otp", config)
        sender = NotificationSender(pusher)
        return sender.process(notification)

    async def async_send_otp(self, notification: OtpNotification, priority: int = 1) -> Dict[str, Any]:
        logger.info(f"Sending OTP notification asynchronously with priority {priority}")
        config = {"priority": priority}
        if "credentials" in self.config:
            config["credentials"] = self.config.get("credentials", {}).get("otp", {})

        pusher = PusherFactory.create_pusher("otp", config)
        sender = NotificationSender(pusher)
        return await sender.async_process(notification)
