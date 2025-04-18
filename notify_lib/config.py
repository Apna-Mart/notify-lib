from pydantic import BaseModel
from typing import List, Dict, Optional


class ProviderConfig(BaseModel):
    name: str
    url: str
    priority: Optional[int] = 1
    credentials: Optional[Dict]
    max_retries: Optional[int] = 3
    timeout: Optional[int] = 30

class SMSConfig(BaseModel):
    providers: List[ProviderConfig]

class EmailConfig(BaseModel):
    providers: List[ProviderConfig]

class NotifyConfig(BaseModel):
    sms: Optional[SMSConfig]
    email: Optional[EmailConfig]
