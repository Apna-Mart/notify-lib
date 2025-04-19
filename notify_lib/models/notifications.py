import uuid
from typing import Optional, List

from notify_lib.constants import MessageType


class Notification:

    def __init__(self, identifier: Optional[str] = None):
        self.identifier: str = identifier or str(uuid.uuid4())
        self.items: List = []

    def add_item(self, item):
        self.items.append(item)
        return self


class SmsNotification(Notification):
    def __init__(
            self, sender_id: Optional[str] = None,
            identifier: Optional[str] = None,
            message_type: MessageType = MessageType.TRANSACTIONAL.value):
        super().__init__(identifier)
        self.sender_id = sender_id
        self.is_unicode = False
        self.message_type = message_type
        self.dlt_data = {}  # For DLT compliance data
        self.template_name = None  # For OTP template


class EmailNotification(Notification):
    def __init__(
            self, from_email: Optional[str] = None,
            subject: Optional[str] = None, identifier: Optional[str] = None):
        super().__init__(identifier)
        self.from_email = from_email
        self.subject = subject
        self.html_content = None
        self.plain_text = None