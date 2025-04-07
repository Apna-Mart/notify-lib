from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> bool:
        pass

    @abstractmethod
    async def async_send(self, to: str, message: str) -> bool:
        pass
