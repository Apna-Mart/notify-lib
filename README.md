# Notify Lib

A custom notification helper to allow sending notifications.

---

## Setup Guide

### Configuration

Create a config object with your vendor credentials:

```python
from config import NotifyConfig
from notification_client import NotificationClient

config = NotifyConfig(
    sms_vendors=[
        {
            "name": "textlocal",
            "api_key": "your_textlocal_api_key",
            "sender_id": "TXTLCL"
        }
    ],
    email_vendors=[
        {
            "name": "sendgrid",
            "api_key": "your_sendgrid_api_key",
            "from_email": "noreply@yourcompany.com"
        }
    ]
)

client = NotificationClient(config)
```

---

## Send Email

```python
from models.notifications import EmailNotification, EmailItem

notification = EmailNotification(
    from_email="noreply@yourcompany.com",
    subject="Welcome",
    html_content="<p>Thank you for registering.</p>",
    items=[
        EmailItem(
            recipient="user@example.com",
            variables={"name": "John"}
        )
    ]
)

result = client.email.send(notification)
```

---

## Send SMS

```python
from models.notifications import SmsNotification, SmsItem
from constants import MessageType

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
