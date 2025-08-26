from enum import Enum


class Channel(Enum):
    SMS = "sms"
    EMAIL = "email"


class MessageType(Enum):
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    OTP = "otp"


class Provider(Enum):
    TWOFACTOR = "twofactor"
    SENDGRID = "sendgrid"