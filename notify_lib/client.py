from notify_lib.config import NotifyConfig
from notify_lib.constants import Channel
from notify_lib.services.service_factory import ServiceFactory


class NotificationClient:

    def __init__(self, config: NotifyConfig):
        self.config = config or {}
        self.sms = ServiceFactory.create_service(Channel.SMS.value, config)
        self.email = ServiceFactory.create_service(Channel.EMAIL.value, config)

