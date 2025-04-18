from typing import Dict, Any, Optional


class NotificationItem:

    def __init__(self, recipient: str, message: str):
        self.recipient = recipient
        self.message = message
        self.delivery_status = "PENDING"
        self.ext_id = None
        self.error = None


class SmsItem(NotificationItem):
    def __init__(self, phone_number: str, message: str, otp: Optional[str] = None):
        super().__init__(phone_number, message)
        self.phone_number = phone_number
        self.otp = otp

    @classmethod
    def create_otp(cls, phone_number: str, otp: str, message: str):
        message = message
        return cls(phone_number, message, otp)


class EmailItem(NotificationItem):
    def __init__(self, email: str, message: str, subject: Optional[str] = None):
        super().__init__(email, message)
        self.email = email
        self.subject = subject
        self.variables = {}
        self.cc = []
        self.bcc = []