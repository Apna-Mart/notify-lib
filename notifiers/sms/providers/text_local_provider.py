from base import BaseNotifier


class TextLocalProvider(BaseNotifier):
    def __init__(self, config):
        self.config = config

    def send(self, to: str, message: str) -> bool:
        print(f"[SMSProvider1] Sending SMS to {to}: {message}")
        return True

    async def async_send(self, to: str, message: str) -> bool:
        return self.send(to, message)