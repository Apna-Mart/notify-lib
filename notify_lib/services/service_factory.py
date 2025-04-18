from notify_lib.config import NotifyConfig
from notify_lib.constants import Channel
from notify_lib.vendors.vendor_factory import VendorFactory
from notify_lib.services.email_service import EmailService
from notify_lib.services.sms_service import SmsService


class ServiceFactory:

    @staticmethod
    def create_service(channel: Channel, config: NotifyConfig):
        config = config or {}
        vendors = VendorFactory.get_vendors(channel, config)
        if channel == Channel.EMAIL.value:
            return EmailService(vendors)
        elif channel == Channel.SMS.value:
            return SmsService(vendors)
        else:
            raise ValueError(f"Unknown Channel: {channel}")
