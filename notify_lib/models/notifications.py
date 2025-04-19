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
            self, identifier: Optional[str] = None,
            message_type: MessageType = MessageType.TRANSACTIONAL.value):
        super().__init__(identifier)
        self.message_type = message_type


class EmailNotification(Notification):

    def __init__(
            self, identifier: Optional[str] = None,
            from_email: Optional[str] = None):
        super().__init__(identifier)
        self.from_email = from_email