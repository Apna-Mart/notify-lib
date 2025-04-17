from pydantic import BaseModel
from typing import Dict, Optional

class ProviderConfig(BaseModel):
    name: str
    url: str
    auth_token: Optional[str] = None
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30

class SMSConfig(BaseModel):
    providers: Dict[int, ProviderConfig]

class EmailConfig(BaseModel):
    providers: Dict[int, ProviderConfig]

class OTPConfig(BaseModel):
    providers: Dict[int, ProviderConfig]

class NotifyConfig(BaseModel):
    sms: SMSConfig
    email: EmailConfig
    otp: OTPConfig
    default_priority: int = 1
