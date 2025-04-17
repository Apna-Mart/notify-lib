import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from logger import logger


def load_env(env_file: Optional[str] = None) -> None:
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
        return

    if os.path.exists(".env"):
        load_dotenv()
        logger.info("Loaded environment from .env")
        return

    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
        logger.info("Loaded environment from .env.local")
        return

    logger.warning("No .env file found. Using system environment variables.")


def get_config_from_env() -> Dict[str, Any]:
    load_env()

    config = {
        "credentials": {
            "sms": {
                "api_key": os.getenv("TWOFACTOR_API_KEY"),
                "sender_id": os.getenv("TWOFACTOR_SENDER_ID"),
                "sms_type": os.getenv("TWOFACTOR_SMS_TYPE", "TRANS_SMS")
            },
            "otp": {
                "template_name": os.getenv("TWOFACTOR_OTP_TEMPLATE", ""),

                "textlocal_api_key": os.getenv("TEXTLOCAL_API_KEY"),
                "textlocal_sender_id": os.getenv("TEXTLOCAL_SENDER_ID")
            },
            "email": {
                "api_key": os.getenv("SENDGRID_API_KEY"),
                "from_email": os.getenv("SENDGRID_FROM_EMAIL")
            }
        }
    }

    log_level = os.getenv("LOG_LEVEL", "INFO")
    if log_level:
        import logging
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    return config