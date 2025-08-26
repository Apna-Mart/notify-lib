from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class ProviderConfig:
    name: str
    priority: int = 1
    credentials: Optional[Dict[str, Any]] = None
    max_retries: int = 3
    timeout: int = 30


@dataclass
class SMSConfig:
    providers: List[ProviderConfig] = field(default_factory=list)


@dataclass
class EmailConfig:
    providers: List[ProviderConfig] = field(default_factory=list)


@dataclass
class NotifyConfig:
    sms: Optional[SMSConfig] = None
    email: Optional[EmailConfig] = None


# ---- Minimal dict -> dataclass builders ----

def provider_from_dict(data: Dict[str, Any]) -> ProviderConfig:
    if not isinstance(data, dict):
        raise ValueError("ProviderConfig must be a dict")
    name = data.get("name")
    return ProviderConfig(
        name=name,
        priority=int(data.get("priority", 1)) if data.get("priority") is not None else 1,
        credentials=data.get("credentials"),
        max_retries=int(data.get("max_retries", 3)) if data.get("max_retries") is not None else 3,
        timeout=int(data.get("timeout", 30)) if data.get("timeout") is not None else 30,
    )


def sms_config_from_dict(data: Dict[str, Any]) -> SMSConfig:
    if not isinstance(data, dict):
        raise ValueError("SMSConfig must be a dict")
    providers = [provider_from_dict(p) for p in data.get("providers", [])]
    return SMSConfig(providers=providers)


def email_config_from_dict(data: Dict[str, Any]) -> EmailConfig:
    if not isinstance(data, dict):
        raise ValueError("EmailConfig must be a dict")
    providers = [provider_from_dict(p) for p in data.get("providers", [])]
    return EmailConfig(providers=providers)


def notify_config_from_dict(data: Dict[str, Any]) -> NotifyConfig:
    if not isinstance(data, dict):
        raise ValueError("NotifyConfig must be a dict")
    sms = sms_config_from_dict(data["sms"]) if data.get("sms") else None
    email = email_config_from_dict(data["email"]) if data.get("email") else None
    return NotifyConfig(sms=sms, email=email)


# ---- Minimal validation ----

def validate_notify_config(cfg: NotifyConfig) -> None:
    if cfg.sms is not None:
        if not isinstance(cfg.sms.providers, list) or len(cfg.sms.providers) == 0:
            raise ValueError("SMSConfig.providers must be a non-empty list when sms config is provided")
        for p in cfg.sms.providers:
            _validate_provider_config(p, channel="sms")
    if cfg.email is not None:
        if not isinstance(cfg.email.providers, list) or len(cfg.email.providers) == 0:
            raise ValueError("EmailConfig.providers must be a non-empty list when email config is provided")
        for p in cfg.email.providers:
            _validate_provider_config(p, channel="email")


def _validate_provider_config(p: ProviderConfig, channel: str) -> None:
    if not isinstance(p.name, str) or not p.name.strip():
        raise ValueError(f"ProviderConfig.name is required for {channel} provider")
    if not isinstance(p.priority, int) or p.priority < 1:
        raise ValueError(f"ProviderConfig.priority must be an integer >= 1 for {channel} provider '{p.name}'")
    if not isinstance(p.max_retries, int) or p.max_retries < 0:
        raise ValueError(f"ProviderConfig.max_retries must be an integer >= 0 for {channel} provider '{p.name}'")
    if not isinstance(p.timeout, int) or p.timeout <= 0:
        raise ValueError(f"ProviderConfig.timeout must be an integer > 0 for {channel} provider '{p.name}'")
    if p.credentials is not None and not isinstance(p.credentials, dict):
        raise ValueError(f"ProviderConfig.credentials must be a dict or None for {channel} provider '{p.name}'")
