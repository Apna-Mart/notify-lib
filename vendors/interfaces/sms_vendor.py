from abc import ABC, abstractmethod
from typing import Dict, Any


class SmsVendor(ABC):

    @abstractmethod
    def configure(self, config: Dict[str, Any]):
        pass

    @abstractmethod
    def send(self, notification) -> str:
        pass

    @abstractmethod
    async def async_send(self, notification) -> str:
        pass