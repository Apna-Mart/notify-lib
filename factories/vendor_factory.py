from vendors.implementations.email.sendgrid import SendGridEmail
from vendors.implementations.otp.textlocal_otp import TextLocalOtp
from vendors.implementations.sms.twofactor import TwoFactorSms


class VendorFactory:

    VENDOR_MAPPINGS = {
        "sms": {
            1: "twofactor",
        },
        "email": {
            1: "sendgrid",

        },
        "otp": {
            1: "textlocal",

        }
    }

    @staticmethod
    def create_vendor(vendor_type, priority=1, config=None):
        config = config or {}

        vendor_mappings = VendorFactory.VENDOR_MAPPINGS.get(vendor_type, {})
        vendor_name = vendor_mappings.get(priority)

        if not vendor_name:
            raise ValueError(f"No vendor configured for type {vendor_type} with priority {priority}")

        vendor = None

        if vendor_type == "sms":
            if vendor_name == "twofactor":
                vendor = TwoFactorSms()
        elif vendor_type == "email":
            if vendor_name == "sendgrid":
                vendor = SendGridEmail()
        elif vendor_type == "otp":
            if vendor_name == "textlocal":
                vendor = TextLocalOtp()

        if vendor:
            vendor.configure(config.get("credentials", {}))
            return vendor

        raise ValueError(f"Vendor {vendor_name} for {vendor_type} not implemented")