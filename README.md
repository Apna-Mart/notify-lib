# Notify Lib

A custom notification helper to allow sending notifications.

---

## Setup Guide

### Configuration

Create a config object with your vendor credentials:

```python
from notify_lib.config import NotifyConfig, ProviderConfig
from notification_client import NotificationClient

config = NotifyConfig(
    sms=SMSConfig(providers=[
        ProviderConfig(
            name="textlocal",
            priority=2,
            credentials={"api_key": api_key, "sender_id": "sender_id"}),
        ProviderConfig(
            name="twofactor",
            priority=1,
            credentials={"api_key": api_key, "sender_id": "sender_id"})]),
    email=EmailConfig(providers=[
        ProviderConfig(
            name= "sendgrid",
            priority=1,
            credentials={"api_key": api_key, "from_email": "from_email"}),
        )
    ])
)

NOTIF_CLIENT = NotificationClient(config)

```

---

## Send Email

```python
from notify_lib.models import EmailNotification, EmailItem

notification = EmailNotification(from_email="noreply@yourcompany.com")

notification.add_item(EmailItem(
    to_email="user@example.com",
    message="<p>Thank you for registering.</p>",
    subject="Welcome",  
    variables={"name": "John"}
))

result = client.email.send(notification)
```

---

## Send SMS

```python
from notify_lib.models import SmsNotification, SmsItem
from notify_lib.constants import MessageType

notification = SmsNotification(
    sender_id="MYAPP",
    message_type=MessageType.TRANSACTIONAL.value,
    items=[
        SmsItem(
            recipient="9198765xxxxx",
            message="Your order #12345 has been shipped."
        )
    ]
)

result = client.sms.send(notification)
```

---

## Send OTP

```python
notification = SmsNotification(
    sender_id="MYAPP",
    message_type=MessageType.OTP.value,
    items=[
        SmsItem(
            recipient="9198765xxxxx",
            message="Your OTP is: {otp}. Valid for 10 minutes.",
            otp="123456"
        )
    ]
)

result = client.sms.send(notification)
```
