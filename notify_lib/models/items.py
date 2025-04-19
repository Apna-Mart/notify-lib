from typing import Optional


class NotificationItem:

    def __init__(self, recipient: str, message: str):
        self.recipient = recipient
        self.message = message
        self.delivery_status = "PENDING"
        self.ext_id = None
        self.error = None


class SmsItem(NotificationItem):
    def __init__(
            self, phone_number: str, message: str, otp: Optional[str] = None,
            template_name: Optional[str] = None, dlt_data: Optional[dict] = None):
        super().__init__(phone_number, message)
        self.otp = otp
        self.template_name = template_name
        self.dlt_data = dlt_data


class EmailItem(NotificationItem):
    def __init__(
            self, to_email: str, message: str,
            subject: Optional[str] = None, variables: Optional[dict] = None,
            cc: Optional[list] = None, bcc: Optional[list] = None):
        super().__init__(to_email, message)
        self.subject = subject
        self.variables = variables
        self.cc = cc
        self.bcc = bcc