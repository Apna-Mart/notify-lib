import requests
import asyncio
import functools

from notify_lib.constants import MessageType
from notify_lib.exceptions import VendorException
from notify_lib.models.notifications import Notification
from notify_lib.vendors.interfaces.sms_vendor import SmsVendor


class TwoFactor(SmsVendor):

    def __init__(self, credentials):
        self.api_key = credentials.get("api_key") if credentials else None
        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "2Factor API key not configured")
        self.sender_id = credentials.get("sender_id") if credentials else None
        self.api_url = "https://2factor.in/API/R1/"  # For SMS
        self.api_url_v1 = "https://2factor.in/API/V1/"  # For OTP
        self.batch_size = 1000
        self.sms_type = None

    def supports_otp(self) -> bool:
        return True

    def send(self, notification):
        if notification.message_type == MessageType.TRANSACTIONAL.value:
            self.sms_type = "TRANS_SMS"
        elif notification.message_type == MessageType.PROMOTIONAL.value:
            self.sms_type = "PROMO_SMS"
        else:
            self.sms_type = "OTP"
        if self.sms_type == "OTP":
            return self._send_otp(notification)
        return self._send_sms(notification)

    def _send_sms(self, notification) -> Notification:
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
                        else:
                            error_msg = response_data.get("Details", "Unknown error")
                            item.delivery_status = "FAILED"
                            item.error = error_msg
                    except (ValueError, KeyError) as e:
                        if "Success" in response.text:
                            item.delivery_status = "SENT"
                            item.ext_id = "2factor_sent"
                        else:
                            item.delivery_status = "FAILED"
                            item.error = f"Invalid response: {response.text}"
                else:
                    error_msg = f"2Factor API error: {response.status_code} - {response.text}"
                    item.delivery_status = "FAILED"
                    item.error = error_msg
            except Exception as e:
                item.delivery_status = "FAILED"
                item.error = str(e)
        return notification

    def _send_otp(self, notification):
        for item in notification.items:
            try:
                if not item.otp:
                    item.delivery_status = "FAILED"
                    item.error = "Missing OTP value"
                    continue
                phone = item.recipient
                if not phone.startswith("+"):
                    if phone.startswith("91"):
                        phone = "+" + phone
                    else:
                        phone = "+91" + phone.lstrip("+")
                template_part = f"/{item.template_name}" if item.template_name else ""
                api_url = f"{self.api_url_v1}{self.api_key}/SMS/{phone}/{item.otp}{template_part}"
                response = requests.get(api_url, params=item.variables)
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        if response_data.get("Status") == "Success":
                            item.delivery_status = "SENT"
                            item.ext_id = str(response_data.get("Details", ""))
                        else:
                            error_msg = response_data.get("Details", "Unknown error")
                            item.delivery_status = "FAILED"
                            item.error = error_msg
                    except (ValueError, KeyError) as e:
                        if "Success" in response.text:
                            item.delivery_status = "SENT"
                            item.ext_id = "2factor_otp_sent"
                        else:
                            item.delivery_status = "FAILED"
                            item.error = f"Invalid response: {response.text}"
                    except Exception as e:
                        item.delivery_status = "FAILED"
                        item.error = str(e)
                else:
                    error_msg = f"2Factor API error: {response.status_code} - {response.text}"
                    item.delivery_status = "FAILED"
                    item.error = error_msg
            except Exception as e:
                item.delivery_status = "FAILED"
                item.error = str(e)
        return notification

    def _send_sms_single_sync(self, item):
        try:
            phone = item.recipient
            if not phone.startswith("91") and not phone.startswith("+91"):
                phone = "91" + phone.lstrip("+")
            payload = {
                "module": self.sms_type,
                "apikey": self.api_key,
                "to": phone,
                "from": self.sender_id,
                "msg": item.message
            }
            if self.sms_type == "TRANS_SMS" and hasattr(item, "dlt_data"):
                dlt_data = getattr(item, "dlt_data", {})
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
                    else:
                        error_msg = response_data.get("Details", "Unknown error")
                        item.delivery_status = "FAILED"
                        item.error = error_msg
                except (ValueError, KeyError):
                    if "Success" in response.text:
                        item.delivery_status = "SENT"
                        item.ext_id = "2factor_sent"
                    else:
                        item.delivery_status = "FAILED"
                        item.error = f"Invalid response: {response.text}"
            else:
                error_msg = f"2Factor API error: {response.status_code} - {response.text}"
                item.delivery_status = "FAILED"
                item.error = error_msg
            return item
        except Exception as e:
            item.delivery_status = "FAILED"
            item.error = str(e)
            return item

    def _send_otp_single_sync(self, item):
        try:
            if not item.otp:
                item.delivery_status = "FAILED"
                item.error = "Missing OTP value"
                return item
            phone = item.recipient
            if not phone.startswith("+"):
                if phone.startswith("91"):
                    phone = "+" + phone
                else:
                    phone = "+91" + phone.lstrip("+")
            template_part = f"/{item.template_name}" if item.template_name else ""
            api_url = f"{self.api_url_v1}{self.api_key}/SMS/{phone}/{item.otp}{template_part}"
            response = requests.get(api_url, params=item.variables)
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get("Status") == "Success":
                        item.delivery_status = "SENT"
                        item.ext_id = str(response_data.get("Details", ""))
                    else:
                        error_msg = response_data.get("Details", "Unknown error")
                        item.delivery_status = "FAILED"
                        item.error = error_msg
                except (ValueError, KeyError):
                    if "Success" in response.text:
                        item.delivery_status = "SENT"
                        item.ext_id = "2factor_otp_sent"
                    else:
                        item.delivery_status = "FAILED"
                        item.error = f"Invalid response: {response.text}"
            else:
                error_msg = f"2Factor API error: {response.status_code} - {response.text}"
                item.delivery_status = "FAILED"
                item.error = error_msg
            return item
        except Exception as e:
            item.delivery_status = "FAILED"
            item.error = str(e)
            return item

    async def send_batch(self, items):
        loop = asyncio.get_running_loop()
        if self.sms_type == "OTP":
            call = self._send_otp_single_sync
        else:
            call = self._send_sms_single_sync
        tasks = [loop.run_in_executor(None, functools.partial(call, item)) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        normalized = []
        for item, result in zip(items, results):
            if isinstance(result, Exception):
                item.delivery_status = "FAILED"
                item.error = str(result)
                normalized.append(item)
            else:
                normalized.append(result)
        return normalized

    async def async_send(self, notification):
        if notification.message_type == MessageType.TRANSACTIONAL.value:
            self.sms_type = "TRANS_SMS"
        elif notification.message_type == MessageType.PROMOTIONAL.value:
            self.sms_type = "PROMO_SMS"
        else:
            self.sms_type = "OTP"
        all_results = []
        for i in range(0, len(notification.items), self.batch_size):
            batch = notification.items[i:i + self.batch_size]
            batch_results = await self.send_batch(batch)
            all_results.extend(batch_results)
        notification.items = all_results
        return notification