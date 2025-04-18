from abc import ABC, abstractmethod

class SmsVendor(ABC):

    @abstractmethod
    def send(self, notification) -> str:
        pass

    @abstractmethod
    async def async_send(self, notification) -> str:
        pass

    def supports_otp(self) -> bool:
        return False