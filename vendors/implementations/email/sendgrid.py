import asyncio

from exceptions import VendorException
from vendors.interfaces.email_vendor import EmailVendor


class SendGridEmail(EmailVendor):

    def __init__(self, credentials):
        self.api_key = credentials.get("api_key") if credentials else None
        self.from_email = credentials.get("from_email") if credentials else None
        self.batch_size = 1000

        try:
            import sendgrid
            from sendgrid.helpers.mail import (
                Mail, Email, To, Content, Personalization,
                Attachment, FileContent, FileName, FileType, Disposition, ContentId
            )
            self.sendgrid = sendgrid
            self.sg_client_class = sendgrid.SendGridAPIClient
            self.mail_class = Mail
            self.email_class = Email
            self.to_class = To
            self.content_class = Content
            self.personalization_class = Personalization
            self.attachment_class = Attachment
            self.file_content_class = FileContent
            self.file_name_class = FileName
            self.file_type_class = FileType
            self.disposition_class = Disposition
            self.content_id_class = ContentId
        except ImportError:
            self.sendgrid = None
            self.sg_client_class = None

    def send(self, notification) -> str:
        if not self.sendgrid:
            raise VendorException("VENDOR_DEPENDENCY_ERROR", "SendGrid package not installed")

        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "SendGrid API key not configured")

        sg = self.sg_client_class(self.api_key)

        from_email = self.email_class(notification.from_email or self.from_email)

        mail = self.mail_class(from_email=from_email, subject=notification.subject)

        if notification.html_content:
            mail.add_content(self.content_class("text/html", notification.html_content))
        if notification.plain_text:
            mail.add_content(self.content_class("text/plain", notification.plain_text))

        if hasattr(notification, 'attachments') and notification.attachments:
            for attachment_data in notification.attachments:
                attachment = self.attachment_class()
                attachment.file_content = self.file_content_class(attachment_data.get("content", ""))
                attachment.file_name = self.file_name_class(attachment_data.get("filename", "attachment"))
                attachment.file_type = self.file_type_class(attachment_data.get("type", "application/octet-stream"))
                attachment.disposition = self.disposition_class(attachment_data.get("disposition", "attachment"))
                if "content_id" in attachment_data:
                    attachment.content_id = self.content_id_class(attachment_data["content_id"])
                mail.add_attachment(attachment)

        for item in notification.items:
            personalization = self.personalization_class()
            to_email = self.to_class(item.email)
            personalization.add_to(to_email)

            if item.subject:
                personalization.subject = item.subject

            for key, value in item.variables.items():
                personalization.add_dynamic_template_data({key: value})

            if hasattr(item, 'cc') and item.cc:
                for cc_email in item.cc:
                    personalization.add_cc(self.email_class(cc_email))

            if hasattr(item, 'bcc') and item.bcc:
                for bcc_email in item.bcc:
                    personalization.add_bcc(self.email_class(bcc_email))

            mail.add_personalization(personalization)

        if hasattr(notification, 'template_id') and notification.template_id:
            mail.template_id = notification.template_id

        results = []

        try:
            response = sg.client.mail.send.post(request_body=mail.get())

            if 200 <= response.status_code < 300:
                for item in notification.items:
                    item.delivery_status = "SENT"
                    item.ext_id = str(response.headers.get("X-Message-Id", ""))
                    results.append(True)
            else:
                error_msg = f"SendGrid API error: {response.status_code} - {response.body}"
                for item in notification.items:
                    item.delivery_status = "FAILED"
                    item.error = error_msg
                    results.append(False)
        except Exception as e:
            for item in notification.items:
                item.delivery_status = "FAILED"
                item.error = str(e)
                results.append(False)

        return "success" if all(results) else "batch not sent"

    async def process_batch(self, batch_items, notification):
        batch_notification = type(notification)()
        batch_notification.from_email = notification.from_email
        batch_notification.subject = notification.subject
        batch_notification.html_content = notification.html_content
        batch_notification.plain_text = notification.plain_text

        if hasattr(notification, 'template_id'):
            batch_notification.template_id = notification.template_id
        if hasattr(notification, 'attachments'):
            batch_notification.attachments = notification.attachments

        batch_notification.items = batch_items

        try:
            result = self.send(batch_notification)
            success = result == "success"
            return [getattr(item, 'delivery_status', 'SENT') == 'SENT' for item in batch_items]
        except Exception as e:
            return [False] * len(batch_items)

    async def async_send(self, notification) -> str:
        if not self.sendgrid:
            raise VendorException("VENDOR_DEPENDENCY_ERROR", "SendGrid package not installed")

        if not self.api_key:
            raise VendorException("VENDOR_CONFIG_ERROR", "SendGrid API key not configured")


        all_results = []

        batches = []
        for i in range(0, len(notification.items), self.batch_size):
            batch = notification.items[i:i + self.batch_size]
            batches.append(batch)

        tasks = []
        for i, batch in enumerate(batches):
            task = self.process_batch(batch, notification)
            tasks.append(task)

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                all_results.extend([False] * self.batch_size)
            else:
                all_results.extend(batch_result)

        success_count = sum(1 for r in all_results if r)
        return "success" if all(all_results) else "batch not sent"