"""TextLocal vendor implementation for both SMS and OTP."""

import requests
import aiohttp
import asyncio
from typing import Dict, Any

from constants import MessageType
from exceptions import VendorException
from logger import logger
from vendors.interfaces.sms_vendor import SmsVendor


class TextLocalUnified(SmsVendor):
    def __init__(self):
        self.api_key = None
        self.api_url = "https://api.textlocal.in/send/"
        self.sender_id = None
        self.batch_size = 1000

    def configure(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key")
        self.sender_id = config.get("sender_id")

    def supports_otp(self) -> bool:
        return True

    def send(self, notification) -> str:
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "TextLocal API key not configured")
        results = []

        for item in notification.items:
            try:
                timeout = (5, 10)

                payload = {
                    "apikey": self.api_key,
                    "numbers": item.recipient,
                    "message": item.message,
                    "sender": notification.sender_id or self.sender_id or "TXTLCL"
                }

                response = requests.post(self.api_url, data=payload, timeout=timeout)
                response_data = response.json() if response.text else {}

                if response.status_code == 200 and "errors" not in response_data:
                    item.delivery_status = "SENT"
                    if "message_id" in response_data:
                        item.ext_id = str(response_data["message_id"])
                    elif "messageId" in response_data:
                        item.ext_id = str(response_data["messageId"])
                    else:
                        item.ext_id = "textlocal_sent"
                    results.append(True)
                else:
                    if "errors" in response_data:
                        error_msg = str(response_data["errors"])
                    else:
                        error_msg = f"TextLocal API error: {response.status_code} - {response.text}"

                    item.delivery_status = "FAILED"
                    item.error = error_msg
                    results.append(False)
                    logger.warning(f"Failed to send SMS to {item.recipient}: {error_msg}")

            except Exception as e:
                item.delivery_status = "FAILED"
                item.error = str(e)
                results.append(False)
                logger.error(f"Error sending SMS to {item.recipient}: {str(e)}")

        return "success" if all(results) else "batch not sent"

    async def send_batch(self, items, notification):
        results = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in items:
                task = self._async_send_single(session, item, notification)
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)

        return results

    async def _async_send_single(self, session, item, notification):
        try:
            timeout = aiohttp.ClientTimeout(connect=5, total=10)

            payload = {
                "apikey": self.api_key,
                "numbers": item.recipient,
                "message": item.message,
                "sender": notification.sender_id or self.sender_id or "TXTLCL"
            }

            async with session.post(self.api_url, data=payload, timeout=timeout) as response:
                response_text = await response.text()
                try:
                    response_data = await response.json()
                except:
                    response_data = {}
                    logger.warning(f"Failed to parse JSON response: {response_text}")

                if response.status == 200 and "errors" not in response_data:
                    item.delivery_status = "SENT"
                    if "message_id" in response_data:
                        item.ext_id = str(response_data["message_id"])
                    elif "messageId" in response_data:
                        item.ext_id = str(response_data["messageId"])
                    else:
                        item.ext_id = "textlocal_sent"
                    return True
                else:
                    if "errors" in response_data:
                        error_msg = str(response_data["errors"])
                    else:
                        error_msg = f"TextLocal API error: {response.status} - {response_text}"

                    item.delivery_status = "FAILED"
                    item.error = error_msg
                    logger.warning(f"Failed to send SMS to {item.recipient}: {error_msg}")
                    return False

        except Exception as e:
            item.delivery_status = "FAILED"
            item.error = str(e)
            logger.error(f"Error sending SMS to {item.recipient}: {str(e)}")
            return False

    async def async_send(self, notification) -> str:
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "TextLocal API key not configured")

        msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"
        logger.info(f"Sending {len(notification.items)} {msg_type} messages via TextLocal")

        all_results = []
        for i in range(0, len(notification.items), self.batch_size):
            batch = notification.items[i:i + self.batch_size]
            logger.info(f"Processing batch {i // self.batch_size + 1}: {len(batch)} messages")

            batch_results = await self.send_batch(batch, notification)
            all_results.extend(batch_results)

        success = all(all_results)
        logger.info(
            f"{msg_type} batch processing complete. Success: {sum(all_results)}, Failed: {len(all_results) - sum(all_results)}")
        return "success" if success else "batch not sent"