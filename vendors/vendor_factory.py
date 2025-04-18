from config import NotifyConfig
from constants import Provider, Channel
from vendors.implementations.email.sendgrid import SendGridEmail
from vendors.implementations.sms.textlocal import TextLocal
from vendors.implementations.sms.twofactor import TwoFactor


class VendorFactory:

    @staticmethod
    def get_vendors(channel: Channel, config: NotifyConfig):
        if channel == Channel.SMS.value:
            sms_providers = config.sms.providers
            if not sms_providers:
                raise ValueError(f"No vendor configured for channel {channel}")
            sms_providers.sort(key = lambda x: x.priority)
            vendor_lst = []
            for e in sms_providers:
                if e.name == Provider.TEXTLOCAL:
                    vendor_lst.append(TextLocal(e.credentials))
                elif e.name == Provider.TWOFACTOR:
                    vendor_lst.append(TwoFactor(e.credentials))
                else:
                    raise ValueError(f"Unknown Vendor {e.name} for channel {channel}")
            return vendor_lst
        elif channel == Channel.EMAIL.value:
            email_providers = config.email.providers
            if not email_providers:
                raise ValueError(f"No vendor configured for channel {channel}")
            email_providers.sort(key = lambda x: x.priority)
            vendor_lst = []
            for e in email_providers:
                if e.name == Provider.SENDGRID:
                    vendor_lst.append(SendGridEmail(e.credentials))
                else:
                    raise ValueError(f"Unknown Vendor {e.name} for channel {channel}")
            return vendor_lst
