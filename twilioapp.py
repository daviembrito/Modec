from twilio.rest import Client

class TwilioClient(Client):
    def __init__(self, account_sid, token, from_number):
        super().__init__(account_sid, token)
        self.from_number = from_number

    def sendImage(self, to_number, image_url, title):
        return self.messages.create(
            from_ = f"whatsapp:{self.from_number}",
            to = f"whatsapp:{to_number}",
            media_url = image_url,
            body = title
        )
