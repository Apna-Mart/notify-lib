import uuid
from typing import Optional, List, Dict


class Notification:

    def __init__(self, id: Optional[str] = None):
        self.id: str = id or str(uuid.uuid4())
        self.items: List = []
        self.original_list: List = []
        self.credentials: Dict = {}

    def add_item(self, item):
        self.items.append(item)
        return self


class SmsNotification(Notification):
    def __init__(self, sender_id: Optional[str] = None, id: Optional[str] = None, message_type: str = "transactional"):
        super().__init__(id)
        self.sender_id = sender_id
        self.is_unicode = False
        self.message_type = message_type
        self.dlt_data = {}  # For DLT compliance data
        self.template_name = None  # For OTP template


class EmailNotification(Notification):
    def __init__(self, from_email: Optional[str] = None, subject: Optional[str] = None, id: Optional[str] = None):
        super().__init__(id)
        self.from_email = from_email
        self.subject = subject
        self.html_content = None
        self.plain_text = None