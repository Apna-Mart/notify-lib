import uuid
from typing import Optional


class Notification:
    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.items = []
        self.original_list = []
        self.credentials = {}

    def add_item(self, item):
        self.items.append(item)


class SmsNotification(Notification):
    def __init__(self, sender_id: Optional[str] = None, id: Optional[str] = None):
        super().__init__(id)
        self.sender_id = sender_id
        self.is_unicode = False


class EmailNotification(Notification):
    def __init__(self, from_email: Optional[str] = None, subject: Optional[str] = None, id: Optional[str] = None):
        super().__init__(id)
        self.from_email = from_email
        self.subject = subject
        self.html_content = None
        self.plain_text = None


class OtpNotification(Notification):
    def __init__(self, id: Optional[str] = None):
        super().__init__(id)
        self.is_unicode = False
