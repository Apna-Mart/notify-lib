from pydantic import BaseModel
from typing import List, Dict


class ProviderConfig(BaseModel):
    name: str
    url: str
    priority: int = 1
    credentials: Dict
    max_retries: int = 3
    timeout: int = 30

class SMSConfig(BaseModel):
    providers: List[ProviderConfig]

class EmailConfig(BaseModel):
    providers: List[ProviderConfig]

class NotifyConfig(BaseModel):
    sms: SMSConfig
    email: EmailConfig
