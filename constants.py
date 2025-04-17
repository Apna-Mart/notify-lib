from enum import Enum


class MessageType(Enum):
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    OTP = "otp"


class Provider(Enum):
    TWOFACTOR = "twofactor"
    TEXTLOCAL = "textlocal"
    SENDGRID = "sendgrid"