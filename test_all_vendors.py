import asyncio
import os
import sys

from client import NotificationClient
from models.items import OtpItem, SmsItem, EmailItem
from models.notifications import OtpNotification, SmsNotification, EmailNotification
from utils.env import get_config_from_env

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import logger

config = get_config_from_env()


async def test_textlocal_otp():
    logger.info("=== Testing TextLocal OTP ===")

    client = NotificationClient(config)

    notification = OtpNotification()
    notification.add_item(OtpItem("9876543210", "123456"))

    result = await client.async_send_otp(notification)

    logger.info(f"OTP Send Result: {result['success']}")
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

    notification = SmsNotification(sender_id=config['credentials']['sms'].get('sender_id', 'NOTIFY'))

    notification.dlt_data = {
        "pe_id": "1234567890",
        "template_id": "987654321"
    }

    notification.add_item(SmsItem("9876543210", "Your account has been verified successfully."))

    result = await client.async_send_sms(notification)

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

    notification = SmsNotification(sender_id=promo_config['credentials']['sms'].get('sender_id', 'NOTIFY'))

    notification.add_item(SmsItem("9876543210", "Get 50% off on all products this weekend! Use code WEEKEND50"))

    result = await client.async_send_sms(notification)

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

    notification = OtpNotification()

    for i in range(1, 2501):
        phone = f"9999{i:06d}"
        otp = f"{i % 1000:03d}"
        notification.add_item(OtpItem(phone, otp))

    logger.info(f"Created notification with {len(notification.items)} recipients")

    result = await client.async_send_otp(notification)

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