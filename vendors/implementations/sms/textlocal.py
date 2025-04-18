import requests
import aiohttp
import asyncio

from constants import MessageType
from exceptions import VendorException
from vendors.interfaces.sms_vendor import SmsVendor


class TextLocal(SmsVendor):
    def __init__(self, credentials):
        self.api_key = credentials.get("api_key") if credentials else None
        self.api_url = "https://api.textlocal.in/send/"
        self.sender_id = credentials.get("sender_id") if credentials else None
        self.batch_size = 1000

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

            except Exception as e:
                item.delivery_status = "FAILED"
                item.error = str(e)
                results.append(False)

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
                "sender": self.sender_id
            }

            async with session.post(self.api_url, data=payload, timeout=timeout) as response:
                response_text = await response.text()
                try:
                    response_data = await response.json()
                except:
                    response_data = {}

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
                    return False

        except Exception as e:
            item.delivery_status = "FAILED"
            item.error = str(e)
            return False

    async def async_send(self, notification) -> str:
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "TextLocal API key not configured")

        msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"

        all_results = []
        for i in range(0, len(notification.items), self.batch_size):
            batch = notification.items[i:i + self.batch_size]

            batch_results = await self.send_batch(batch, notification)
            all_results.extend(batch_results)

        success = all(all_results)
        return "success" if success else "batch not sent"