class NotificationException(Exception):
    def __init__(self, short_msg, message):
        self.short_msg = short_msg
        super().__init__(message)

class VendorException(NotificationException):
    pass

