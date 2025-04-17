from typing import Dict, Any, Optional

from constants import MessageType, Provider
from logger import logger
from vendors.implementations.email.sendgrid import SendGridEmail
from vendors.implementations.sms.textlocal import TextLocalUnified
from vendors.implementations.sms.twofactor import TwoFactorUnified


class UnifiedVendorFactory:
    VENDOR_MAPPINGS = {
        MessageType.TRANSACTIONAL.value: {
            1: Provider.TWOFACTOR.value,
            2: Provider.TEXTLOCAL.value,
        },
        MessageType.PROMOTIONAL.value: {
            1: Provider.TWOFACTOR.value,
            2: Provider.TEXTLOCAL.value,
        },
        MessageType.OTP.value: {
            1: Provider.TWOFACTOR.value,
            2: Provider.TEXTLOCAL.value,
        }
    }

    EMAIL_VENDOR_MAPPINGS = {
        1: Provider.SENDGRID.value,
    }

    @staticmethod
    def create_vendor(message_type: str, priority: int = 1, config: Optional[Dict[str, Any]] = None):
        logger.debug(f"Creating vendor for message type: {message_type}, priority: {priority}")
        config = config or {}

        vendor_mappings = UnifiedVendorFactory.VENDOR_MAPPINGS.get(message_type, {})
        vendor_name = vendor_mappings.get(priority)

        if not vendor_name:
            logger.warning(f"No vendor configured for message type {message_type} with priority {priority}")
            raise ValueError(f"No vendor configured for message type {message_type} with priority {priority}")

        vendor = None

        if vendor_name == Provider.TWOFACTOR.value:
            vendor = TwoFactorUnified()
            if message_type == MessageType.PROMOTIONAL.value:
                vendor.set_sms_type("PROMO_SMS")
            else:
                vendor.set_sms_type("TRANS_SMS")
        elif vendor_name == Provider.TEXTLOCAL.value:
            vendor = TextLocalUnified()

        if vendor:
            creds = config.get("credentials", {}).get("sms", {})

            if vendor_name == Provider.TEXTLOCAL.value and message_type == MessageType.OTP.value:
                otp_creds = config.get("credentials", {}).get("otp", {})
                if "textlocal_api_key" in otp_creds:
                    creds = {
                        "api_key": otp_creds.get("textlocal_api_key"),
                        "sender_id": otp_creds.get("textlocal_sender_id")
                    }

            if vendor_name == Provider.TWOFACTOR.value and message_type == MessageType.OTP.value:
                otp_creds = config.get("credentials", {}).get("otp", {})
                if "template_name" in otp_creds:
                    creds["template_name"] = otp_creds.get("template_name")

            vendor.configure(creds)
            logger.info(f"Created and configured {vendor_name} vendor for {message_type}")
            return vendor

        logger.warning(f"Vendor {vendor_name} not implemented")
        raise ValueError(f"Vendor {vendor_name} not implemented")

    @staticmethod
    def create_email_vendor(priority: int = 1, config: Optional[Dict[str, Any]] = None):
        config = config or {}

        vendor_name = UnifiedVendorFactory.EMAIL_VENDOR_MAPPINGS.get(priority)

        if not vendor_name:
            logger.warning(f"No email vendor configured with priority {priority}")
            raise ValueError(f"No email vendor configured with priority {priority}")

        vendor = None

        if vendor_name == Provider.SENDGRID.value:
            vendor = SendGridEmail()

        if vendor:
            creds = config.get("credentials", {}).get("email", {})
            vendor.configure(creds)
            logger.info(f"Created and configured {vendor_name} email vendor")
            return vendor

        logger.warning(f"Email vendor {vendor_name} not implemented")
        raise ValueError(f"Email vendor {vendor_name} not implemented")