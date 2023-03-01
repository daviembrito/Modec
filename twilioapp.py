from twilio.rest import Client

class TwilioClient(Client):
    def __init__(self, account_sid, token):
        super().__init__(account_sid, token)
        self.from_number = "+14155238886"

    def sendImage(self, to_number, image_url, title):
        return self.messages.create(
            from_ = f"whatsapp:{self.from_number}",
            to = f"whatsapp:{to_number}",
            media_url = image_url,
            body = title
        )
