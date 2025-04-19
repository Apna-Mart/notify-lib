from notify_lib.config import NotifyConfig
from notify_lib.constants import Channel
from notify_lib.services.lazy_service import LazyService
from notify_lib.services.service_factory import ServiceFactory


class NotificationClient:

    def __init__(self, config: NotifyConfig):
        self.config = config or {}

    sms = LazyService(lambda self: ServiceFactory.create_service(Channel.SMS.value, self.config))
    email = LazyService(lambda self: ServiceFactory.create_service(Channel.EMAIL.value, self.config))

