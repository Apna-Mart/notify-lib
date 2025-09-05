from notify_lib.config import NotifyConfig, notify_config_from_dict, validate_notify_config
from notify_lib.constants import Channel
from notify_lib.vendors.vendor_factory import VendorFactory
from notify_lib.services.email_service import EmailService
from notify_lib.services.sms_service import SmsService
from typing import Any


class ServiceFactory:

    @staticmethod
    def create_service(channel: Channel, config: Any):
        # Normalize config to NotifyConfig and validate
        if isinstance(config, dict):
            config = notify_config_from_dict(config)
        elif not isinstance(config, NotifyConfig):
            raise ValueError("config must be a NotifyConfig or dict")
        validate_notify_config(config)

        # Ensure the requested channel is configured
        if channel == Channel.SMS.value and (config.sms is None):
            raise ValueError("No SMS configuration provided")
        if channel == Channel.EMAIL.value and (config.email is None):
            raise ValueError("No Email configuration provided")

        vendors = VendorFactory.get_vendors(channel, config)
        if channel == Channel.EMAIL.value:
            return EmailService(vendors)
        elif channel == Channel.SMS.value:
            return SmsService(vendors)
        else:
            raise ValueError(f"Unknown Channel: {channel}")
