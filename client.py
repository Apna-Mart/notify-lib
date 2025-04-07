# notify_lib/client.py

from config import NotifyConfig
from notifiers.sms.providers.text_local_provider import TextLocalProvider
from notifiers.email.providers.smtp_provider import SMTPProvider

class NotificationClient:
    def __init__(self, config: NotifyConfig):
        self.sms = TextLocalProvider(config.sms.providers[0])
        self.email = SMTPProvider(config.email.providers[0])

    def send_sms(self, to, message):
        return self.sms.send(to, message)

    def send_email(self, to, message):
        return self.email.send(to, message)
