import requests
import aiohttp
import asyncio
from typing import Dict, Any, Literal

from exceptions import VendorException
from logger import logger
from vendors.interfaces.sms_vendor import SmsVendor


class TwoFactorSms(SmsVendor):
    def __init__(self):
        self.api_key = None
        self.sender_id = None
        self.api_url = "https://2factor.in/API/R1/"
        self.sms_type = "TRANS_SMS"
        self.batch_size = 1000

    def configure(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key")
        self.sender_id = config.get("sender_id")
        self.sms_type = config.get("sms_type", "TRANS_SMS")  # TRANS_SMS or PROMO_SMS

    def set_sms_type(self, sms_type: Literal["TRANS_SMS", "PROMO_SMS"]):
        if sms_type not in ["TRANS_SMS", "PROMO_SMS"]:
            raise ValueError("SMS type must be either 'TRANS_SMS' or 'PROMO_SMS'")
        self.sms_type = sms_type

    def send(self, notification) -> str:
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "2Factor API key not configured")

        results = []

        for item in notification.items:
            try:
                phone = item.recipient
                if not phone.startswith("91") and not phone.startswith("+91"):
                    phone = "91" + phone.lstrip("+")

                payload = {
                    "module": self.sms_type,
                    "apikey": self.api_key,
                    "to": phone,
                    "from": notification.sender_id or self.sender_id or "HEADER",
                    "msg": item.message
                }

                if self.sms_type == "TRANS_SMS" and hasattr(notification, "dlt_data"):
                    dlt_data = getattr(notification, "dlt_data", {})
                    if "pe_id" in dlt_data:
                        payload["peid"] = dlt_data["pe_id"]
                    if "template_id" in dlt_data:
                        payload["ctid"] = dlt_data["template_id"]

                response = requests.post(self.api_url, data=payload)

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        if response_data.get("Status") == "Success":
                            item.delivery_status = "SENT"
                            item.ext_id = str(response_data.get("Details", ""))
                            results.append(True)
                        else:
                            error_msg = response_data.get("Details", "Unknown error")
                            item.delivery_status = "FAILED"
                            item.error = error_msg
                            results.append(False)
                            logger.warning(f"Failed to send SMS to {item.recipient}: {error_msg}")
                    except (ValueError, KeyError) as e:
                        if "Success" in response.text:
                            item.delivery_status = "SENT"
                            item.ext_id = "2factor_sent"
                            results.append(True)
                        else:
                            item.delivery_status = "FAILED"
                            item.error = f"Invalid response: {response.text}"
                            results.append(False)
                            logger.warning(f"Failed to parse 2Factor response for {item.recipient}: {response.text}")
                else:
                    error_msg = f"2Factor API error: {response.status_code} - {response.text}"
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
            phone = item.recipient
            if not phone.startswith("91") and not phone.startswith("+91"):
                phone = "91" + phone.lstrip("+")

            payload = {
                "module": self.sms_type,
                "apikey": self.api_key,
                "to": phone,
                "from": notification.sender_id or self.sender_id or "HEADER",
                "msg": item.message
            }

            if self.sms_type == "TRANS_SMS" and hasattr(notification, "dlt_data"):
                dlt_data = getattr(notification, "dlt_data", {})
                if "pe_id" in dlt_data:
                    payload["peid"] = dlt_data["pe_id"]
                if "template_id" in dlt_data:
                    payload["ctid"] = dlt_data["template_id"]

            async with session.post(self.api_url, data=payload) as response:
                response_text = await response.text()

                if response.status == 200:
                    try:
                        response_data = await response.json()
                        if response_data.get("Status") == "Success":
                            item.delivery_status = "SENT"
                            item.ext_id = str(response_data.get("Details", ""))
                            return True
                        else:
                            error_msg = response_data.get("Details", "Unknown error")
                            item.delivery_status = "FAILED"
                            item.error = error_msg
                            logger.warning(f"Failed to send SMS to {item.recipient}: {error_msg}")
                            return False
                    except (ValueError, KeyError) as e:
                        if "Success" in response_text:
                            item.delivery_status = "SENT"
                            item.ext_id = "2factor_sent"
                            return True
                        else:
                            item.delivery_status = "FAILED"
                            item.error = f"Invalid response: {response_text}"
                            logger.warning(f"Failed to parse 2Factor response for {item.recipient}: {response_text}")
                            return False
                else:
                    error_msg = f"2Factor API error: {response.status} - {response_text}"
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
            raise VendorException("VENDOR_CONFIG_ERROR", "2Factor API key not configured")

        logger.info(f"Sending {len(notification.items)} SMS messages via 2Factor (Type: {self.sms_type})")

        all_results = []
        for i in range(0, len(notification.items), self.batch_size):
            batch = notification.items[i:i + self.batch_size]
            logger.info(f"Processing batch {i // self.batch_size + 1}: {len(batch)} messages")

            batch_results = await self.send_batch(batch, notification)
            all_results.extend(batch_results)

        success = all(all_results)
        logger.info(
            f"SMS batch processing complete. Success: {sum(all_results)}, Failed: {len(all_results) - sum(all_results)}")
        return "success" if success else "batch not sent"