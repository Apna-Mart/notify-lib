from pydantic import BaseModel
from typing import List

class ProviderConfig(BaseModel):
    name: str
    url: str
    auth_token: str
    max_retries: int = 3

class SMSConfig(BaseModel):
    providers: List[ProviderConfig]

class EmailConfig(BaseModel):
    providers: List[ProviderConfig]

class FCMConfig(BaseModel):
    api_key: str

class MQTTConfig(BaseModel):
    broker_url: str
    port: int
    username: str
    password: str

class NotifyConfig(BaseModel):
    sms: SMSConfig
    email: EmailConfig
    fcm: FCMConfig
    mqtt: MQTTConfig
