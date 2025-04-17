from factories.vendor_factory import VendorFactory
from pushers.email_pusher import EmailPusher
from pushers.otp_pusher import OtpPusher
from pushers.sms_pusher import SmsPusher

class PusherFactory:

    @staticmethod
    def create_pusher(notification_type, config=None):
        config = config or {}
        priority = config.get("priority", 1)

        vendor = VendorFactory.create_vendor(notification_type, priority, config)

        if notification_type == "sms":
            return SmsPusher(vendor)
        elif notification_type == "email":
            return EmailPusher(vendor)
        elif notification_type == "otp":
            return OtpPusher(vendor)
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")