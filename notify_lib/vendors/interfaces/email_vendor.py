from abc import ABC, abstractmethod


class EmailVendor(ABC):

    @abstractmethod
    def send(self, notification) -> str:
        pass

    @abstractmethod
    async def async_send(self, notification) -> str:
        pass