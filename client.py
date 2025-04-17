from logger import logger
from config import NotifyConfig
from constants import Channel
from services.service_factory import ServiceFactory


class NotificationClient:

    def __init__(self, config: NotifyConfig):
        self.config = config or {}
        logger.info("NotificationClient initialized")
        self.sms = ServiceFactory.create_service(Channel.SMS.value, config)
        self.email = ServiceFactory.create_service(Channel.EMAIL.value, config)

