"""Unified factory for creating pushers."""

from typing import Dict, Any, Optional

from constants import MessageType
from factories.vendor_factory import UnifiedVendorFactory
from logger import logger
from pushers.email_pusher import EmailPusher
from pushers.sms_pusher import SmsUnifiedPusher


class UnifiedPusherFactory:

    @staticmethod
    def create_pusher(message_type: str, config: Optional[Dict[str, Any]] = None):
        logger.debug(f"Creating pusher for message type: {message_type}")
        config = config or {}
        priority = config.get("priority", 1)

        try:
            if message_type == "email":
                vendor = UnifiedVendorFactory.create_email_vendor(priority, config)
                return EmailPusher(vendor)

            if message_type in [MessageType.TRANSACTIONAL.value, MessageType.PROMOTIONAL.value, MessageType.OTP.value]:
                vendor = UnifiedVendorFactory.create_vendor(message_type, priority, config)
                return SmsUnifiedPusher(vendor)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                raise ValueError(f"Unknown message type: {message_type}")

        except ValueError as e:
            logger.warning(f"Error creating pusher: {str(e)}")
            raise ValueError(f"Error creating pusher: {str(e)}")