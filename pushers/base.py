from abc import ABC, abstractmethod
from logger import logger


class NotificationPusher(ABC):
    @abstractmethod
    def send(self, notification):
        pass

    @abstractmethod
    async def async_send(self, notification):
        pass

    @abstractmethod
    def safety_check(self, notification) -> bool:
        pass

    @abstractmethod
    def get_notification_class(self):
        pass

    def process(self, notification):
        self.prepare(notification)

        if not self.safety_check(notification):
            logger.warning(f"Notification failed safety check: {type(notification).__name__}")
            return False

        logger.info(f"Sending {type(notification).__name__} with {len(notification.items)} recipients")
        result = self.send(notification)

        self.post_process(notification, result)

        return result

    async def async_process(self, notification):
        self.prepare(notification)

        if not self.safety_check(notification):
            logger.warning(f"Notification failed async safety check: {type(notification).__name__}")
            return False

        logger.info(f"Sending {type(notification).__name__} asynchronously with {len(notification.items)} recipients")
        result = await self.async_send(notification)

        self.post_process(notification, result)

        return result

    def prepare(self, notification):
        pass

    def post_process(self, notification, result):
        success_count = sum(1 for item in notification.items if getattr(item, 'delivery_status', '') == 'SENT')
        failure_count = len(notification.items) - success_count

        if success_count == len(notification.items):
            logger.info(f"All {success_count} messages delivered successfully")
        else:
            logger.warning(f"Partial delivery: {success_count} succeeded, {failure_count} failed")