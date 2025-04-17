import requests
import aiohttp
import asyncio
from typing import Dict, Any,Literal

from constants import MessageType
from exceptions import VendorException
from logger import logger
from vendors.interfaces.sms_vendor import SmsVendor


class TwoFactorUnified(SmsVendor):

    def __init__(self):
        self.api_key = None
        self.sender_id = None
        self.api_url = "https://2factor.in/API/R1/"  # For SMS
        self.api_url_v1 = "https://2factor.in/API/V1/"  # For OTP
        self.sms_type = "TRANS_SMS"  # Default to transactional
        self.template_name = None
        self.batch_size = 1000

    def configure(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key")
        self.sender_id = config.get("sender_id")
        self.sms_type = config.get("sms_type", "TRANS_SMS")
        self.template_name = config.get("template_name", "")

    def set_sms_type(self, sms_type: Literal["TRANS_SMS", "PROMO_SMS"]):
        if sms_type not in ["TRANS_SMS", "PROMO_SMS"]:
            raise ValueError("SMS type must be either 'TRANS_SMS' or 'PROMO_SMS'")
        self.sms_type = sms_type

    def supports_otp(self) -> bool:
        return True

    def send(self, notification) -> str:
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "2Factor API key not configured")

        if notification.message_type == MessageType.OTP.value:
            return self._send_otp(notification)
        else:
            return self._send_sms(notification)

    def _send_sms(self, notification) -> str:
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

    def _send_otp(self, notification) -> str:
        results = []

        for item in notification.items:
            try:
                if not item.otp:
                    item.delivery_status = "FAILED"
                    item.error = "Missing OTP value"
                    results.append(False)
                    logger.warning(f"Missing OTP for recipient: {item.recipient}")
                    continue

                phone = item.recipient
                if not phone.startswith("+"):
                    if phone.startswith("91"):
                        phone = "+" + phone
                    else:
                        phone = "+91" + phone.lstrip("+")

                template_part = f"/{self.template_name}" if self.template_name else ""
                api_url = f"{self.api_url_v1}{self.api_key}/SMS/{phone}/{item.otp}{template_part}"

                response = requests.get(api_url)

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        if response_data.get("Status") == "Success":
                            item.delivery_status = "SENT"
                            item.ext_id = str(response_data.get("Details", ""))
                            results.append(True)
                            logger.info(f"Successfully sent OTP to {item.recipient}")
                        else:
                            error_msg = response_data.get("Details", "Unknown error")
                            item.delivery_status = "FAILED"
                            item.error = error_msg
                            results.append(False)
                            logger.warning(f"Failed to send OTP to {item.recipient}: {error_msg}")
                    except (ValueError, KeyError) as e:
                        if "Success" in response.text:
                            item.delivery_status = "SENT"
                            item.ext_id = "2factor_otp_sent"
                            results.append(True)
                            logger.info(f"Successfully sent OTP to {item.recipient}")
                        else:
                            item.delivery_status = "FAILED"
                            item.error = f"Invalid response: {response.text}"
                            results.append(False)
                            logger.warning(
                                f"Failed to parse 2Factor OTP response for {item.recipient}: {response.text}")
                    except Exception as e:
                        item.delivery_status = "FAILED"
                        item.error = str(e)
                        results.append(False)
                        logger.error(f"Error processing 2Factor OTP response for {item.recipient}: {str(e)}")
                else:
                    error_msg = f"2Factor API error: {response.status_code} - {response.text}"
                    item.delivery_status = "FAILED"
                    item.error = error_msg
                    results.append(False)
                    logger.warning(f"Failed to send OTP to {item.recipient}: {error_msg}")
            except Exception as e:
                item.delivery_status = "FAILED"
                item.error = str(e)
                results.append(False)
                logger.error(f"Error sending OTP to {item.recipient}: {str(e)}")

        return "success" if all(results) else "batch not sent"

    async def send_batch(self, items, notification):
        results = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in items:
                if notification.message_type == MessageType.OTP.value and item.otp:
                    task = self._async_send_otp_single(session, item, notification)
                else:
                    task = self._async_send_sms_single(session, item, notification)
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)

        return results

    async def _async_send_sms_single(self, session, item, notification):
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

    async def _async_send_otp_single(self, session, item, notification):
        try:
            if not item.otp:
                item.delivery_status = "FAILED"
                item.error = "Missing OTP value"
                logger.warning(f"Missing OTP for recipient: {item.recipient}")
                return False

            phone = item.recipient
            if not phone.startswith("+"):
                if phone.startswith("91"):
                    phone = "+" + phone
                else:
                    phone = "+91" + phone.lstrip("+")

            template_part = f"/{self.template_name}" if self.template_name else ""
            api_url = f"{self.api_url_v1}{self.api_key}/SMS/{phone}/{item.otp}{template_part}"

            async with session.get(api_url) as response:
                response_text = await response.text()

                if response.status == 200:
                    try:
                        response_data = await response.json()
                        if response_data.get("Status") == "Success":
                            item.delivery_status = "SENT"
                            item.ext_id = str(response_data.get("Details", ""))
                            logger.info(f"Successfully sent OTP to {item.recipient}")
                            return True
                        else:
                            error_msg = response_data.get("Details", "Unknown error")
                            item.delivery_status = "FAILED"
                            item.error = error_msg
                            logger.warning(f"Failed to send OTP to {item.recipient}: {error_msg}")
                            return False
                    except (ValueError, KeyError) as e:
                        if "Success" in response_text:
                            item.delivery_status = "SENT"
                            item.ext_id = "2factor_otp_sent"
                            logger.info(f"Successfully sent OTP to {item.recipient}")
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
                    logger.warning(f"Failed to send OTP to {item.recipient}: {error_msg}")
                    return False
        except Exception as e:
            item.delivery_status = "FAILED"
            item.error = str(e)
            logger.error(f"Error sending OTP to {item.recipient}: {str(e)}")
            return False

    async def async_send(self, notification) -> str:
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "2Factor API key not configured")

        msg_type = "OTP" if notification.message_type == MessageType.OTP.value else "SMS"
        logger.info(f"Sending {len(notification.items)} {msg_type} messages via 2Factor")

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