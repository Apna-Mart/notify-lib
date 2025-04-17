from typing import Dict, Any
from logger import logger


class NotificationSender:
    def __init__(self, pusher):
        self.pusher = pusher

    def process(self, notification) -> Dict[str, Any]:
        try:
            for item in notification.items:
                item.delivery_status = "SEND_FAILED"

            notification.original_list = notification.items.copy()

            if self.pusher.safety_check(notification):
                logger.info(f"Sending notification with {len(notification.items)} items")

                ext_id = self.pusher.send(notification)

                success_count = sum(1 for item in notification.items if item.delivery_status == "SENT")
                logger.info(f"Notification sent. Success: {success_count}/{len(notification.items)}")

                return {
                    "success": True,
                    "ext_id": ext_id,
                    "items": [
                        {
                            "recipient": item.recipient,
                            "status": item.delivery_status,
                            "ext_id": item.ext_id,
                            "error": item.error
                        } for item in notification.items
                    ]
                }
            else:
                logger.warning("Notification failed safety check")
                return {"success": False, "reason": "Failed safety check"}

        except Exception as e:
            logger.error(f"Error processing notification: {str(e)}")
            return {"success": False, "error": str(e)}

    async def async_process(self, notification) -> Dict[str, Any]:
        try:
            for item in notification.items:
                item.delivery_status = "SEND_FAILED"

            notification.original_list = notification.items.copy()

            if self.pusher.safety_check(notification):
                logger.info(f"Sending notification asynchronously with {len(notification.items)} items")

                ext_id = await self.pusher.async_send(notification)

                success_count = sum(1 for item in notification.items if item.delivery_status == "SENT")
                logger.info(f"Notification sent asynchronously. Success: {success_count}/{len(notification.items)}")

                return {
                    "success": True,
                    "ext_id": ext_id,
                    "items": [
                        {
                            "recipient": item.recipient,
                            "status": item.delivery_status,
                            "ext_id": item.ext_id,
                            "error": item.error
                        } for item in notification.items
                    ]
                }
            else:
                logger.warning("Notification failed safety check")
                return {"success": False, "reason": "Failed safety check"}

        except Exception as e:
            logger.error(f"Error processing notification asynchronously: {str(e)}")
            return {"success": False, "error": str(e)}