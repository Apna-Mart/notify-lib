from abc import ABC, abstractmethod


class NotificationService(ABC):
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
            return False

        result = self.send(notification)

        self.post_process(notification, result)

        return result

    async def async_process(self, notification):
        self.prepare(notification)

        if not self.safety_check(notification):
            return False

        result = await self.async_send(notification)

        self.post_process(notification, result)

        return result

    def prepare(self, notification):
        pass

    def post_process(self, notification, result):
        success_count = sum(1 for item in notification.items if getattr(item, 'delivery_status', '') == 'SENT')
        failure_count = len(notification.items) - success_count

        status = 'SUCCESS' if success_count == len(notification.items) else 'PARTIAL_FAILURE'

        return {
            'status': status,
            'success_count': success_count,
            'failure_count': failure_count
        }
