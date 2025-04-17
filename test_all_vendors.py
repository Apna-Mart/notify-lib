import asyncio
import os
import sys

from client import NotificationClient
from constants import MessageType
from models.items import SmsItem, EmailItem
from models.notifications import SmsNotification, EmailNotification
from utils.env import get_config_from_env

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import logger

config = get_config_from_env()


async def test_textlocal_otp():
    logger.info("=== Testing TextLocal OTP ===")

    client = NotificationClient(config)

    notification = SmsNotification(
        sender_id=config['credentials']['otp'].get('textlocal_sender_id', 'TXTLCL'),
        message_type=MessageType.OTP.value
    )

    otp_code = "123456"
    otp_message = f"Your Apna Mart OTP is {otp_code}. It will expire in the next 5 mins:\nID: uKCuIPa/aTE"

    notification.add_item(SmsItem("8839000758", otp_message, otp_code))

    result = await client.async_send_sms(notification, priority=2)

    logger.info(f"TextLocal OTP Send Result: {result['success']}")
    if not result['success']:
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
    else:
        for item_result in result.get('items', []):
            logger.info(f"  - {item_result['recipient']}: {item_result['status']}")
            if item_result['status'] != 'SENT':
                logger.warning(f"    Error: {item_result.get('error', 'Unknown error')}")


async def test_2factor_otp():
    logger.info("=== Testing 2Factor OTP ===")

    template_name = config['credentials']['otp'].get('template_name', '')

    client = NotificationClient(config)

    notification = SmsNotification(
        sender_id=config['credentials']['sms'].get('sender_id', 'NOTIFY'),
        message_type=MessageType.OTP.value
    )

    notification.template_name = template_name

    phone_number = "9876543210"
    otp_code = "123456"

    notification.add_item(SmsItem(phone_number, f"Your verification code is {otp_code}", otp_code))

    result = await client.async_send_sms(notification, priority=1)

    logger.info(f"2Factor OTP Send Result: {result['success']}")
    if not result['success']:
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
    else:
        for item_result in result.get('items', []):
            logger.info(f"  - {item_result['recipient']}: {item_result['status']}")
            if item_result['status'] != 'SENT':
                logger.warning(f"    Error: {item_result.get('error', 'Unknown error')}")


async def test_2factor_sms_transactional():
    logger.info("=== Testing 2Factor SMS (Transactional) ===")

    client = NotificationClient(config)

    notification = SmsNotification(
        sender_id=config['credentials']['sms'].get('sender_id', 'NOTIFY'),
        message_type=MessageType.TRANSACTIONAL.value
    )

    notification.dlt_data = {
        "pe_id": "1234567890",
        "template_id": "987654321"
    }

    notification.add_item(SmsItem("9876543210", "Your account has been verified successfully."))

    result = await client.async_send_sms(notification, priority=1)

    logger.info(f"Transactional SMS Result: {result['success']}")
    if not result['success']:
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
    else:
        for item_result in result.get('items', []):
            logger.info(f"  - {item_result['recipient']}: {item_result['status']}")
            if item_result['status'] != 'SENT':
                logger.warning(f"    Error: {item_result.get('error', 'Unknown error')}")


async def test_2factor_sms_promotional():
    logger.info("=== Testing 2Factor SMS (Promotional) ===")

    promo_config = config.copy()
    promo_config['credentials']['sms']['sms_type'] = 'PROMO_SMS'

    client = NotificationClient(promo_config)

    notification = SmsNotification(
        sender_id=promo_config['credentials']['sms'].get('sender_id', 'NOTIFY'),
        message_type=MessageType.PROMOTIONAL.value
    )

    notification.add_item(SmsItem("9876543210", "Get 50% off on all products this weekend! Use code WEEKEND50"))

    result = await client.async_send_sms(notification, priority=1)

    logger.info(f"Promotional SMS Result: {result['success']}")
    if not result['success']:
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
    else:
        for item_result in result.get('items', []):
            logger.info(f"  - {item_result['recipient']}: {item_result['status']}")
            if item_result['status'] != 'SENT':
                logger.warning(f"    Error: {item_result.get('error', 'Unknown error')}")


async def test_sendgrid_email():
    logger.info("=== Testing SendGrid Email ===")

    client = NotificationClient(config)

    notification = EmailNotification(
        from_email=config['credentials']['email'].get('from_email', 'test@example.com'),
        subject="Test Email from Notification Library"
    )

    notification.html_content = """
    <html>
    <body>
        <h1>Test Email</h1>
        <p>This is a test email from the notification library.</p>
    </body>
    </html>
    """

    notification.plain_text = "Test Email\n\nThis is a test email from the notification library."

    notification.add_item(EmailItem("recipient@example.com", ""))

    result = await client.async_send_email(notification)

    logger.info(f"Email Send Result: {result['success']}")
    if not result['success']:
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
    else:
        for item_result in result.get('items', []):
            logger.info(f"  - {item_result['recipient']}: {item_result['status']}")
            if item_result['status'] != 'SENT':
                logger.warning(f"    Error: {item_result.get('error', 'Unknown error')}")


async def test_batch_processing():
    logger.info("=== Testing Batch Processing ===")

    client = NotificationClient(config)

    notification = SmsNotification(
        sender_id=config['credentials']['sms'].get('sender_id', 'NOTIFY'),
        message_type=MessageType.OTP.value
    )

    for i in range(1, 10):
        phone = "8839000758"
        otp = f"{100000 + (i % 900000):06d}"
        message = f"Your Apna Mart OTP is {otp}. It will expire in the next 5 mins: ID: uKCuIPa/aTE"
        notification.add_item(SmsItem(phone, message, otp))

    logger.info(f"Created notification with {len(notification.items)} recipients")

    result = await client.async_send_sms(notification)

    logger.info(f"Batch Processing Result: {result['success']}")
    if not result['success']:
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
    else:
        successes = sum(1 for item in result.get('items', []) if item['status'] == 'SENT')
        failures = sum(1 for item in result.get('items', []) if item['status'] != 'SENT')
        logger.info(f"  Success: {successes}, Failed: {failures}")


async def run_all_tests():
    try:
        await test_textlocal_otp()

        await test_2factor_otp()

        await test_2factor_sms_transactional()

        await test_2factor_sms_promotional()

        await test_sendgrid_email()

        await test_batch_processing()

    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(run_all_tests())