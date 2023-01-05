from django.conf import settings
from twilio.rest import Client 
import json

def send_one_way_message(sender_number, message):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create( 
                                from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',  
                                body=message,      
                                to=f'whatsapp:{sender_number}'  
                            ) 
    
    response = message.sid
    print(response)

    # Response format
    """
    {
        "body": "Your Twilio code is 1238432",
        "num_segments": "1",
        "direction": "outbound-api",
        "from": "whatsapp:+14155238886",
        "date_updated": "Wed, 04 Jan 2023 14:05:49 +0000",
        "price": null,
        "error_message": null,
        "uri": "/2010-04-01/Accounts/AC1463d34872ec53122a2fb0dd7148521e/Messages/SM942c0d4b56ca4035b2da454d2b7f94b2.json",
        "account_sid": "AC1463d34872ec53122a2fb0dd7148521e",
        "num_media": "0",
        "to": "whatsapp:+917699419499",
        "date_created": "Wed, 04 Jan 2023 14:05:49 +0000",
        "status": "queued",
        "sid": "SM942c0d4b56ca4035b2da454d2b7f94b2",
        "date_sent": null,
        "messaging_service_sid": null,
        "error_code": null,
        "price_unit": null,
        "api_version": "2010-04-01",
        "subresource_uris": {
            "media": "/2010-04-01/Accounts/AC1463d34872ec53122a2fb0dd7148521e/Messages/SM942c0d4b56ca4035b2da454d2b7f94b2/Media.json"
        }
    }
    """


def two_way_message(sender_number, message):
    #It has 24 hours timeline to make a conversation
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token) 
 
    message = client.messages.create( 
                                from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',  
                                body=message,      
                                to=f'whatsapp:{sender_number}' 
                            ) 
    
    response = message.sid
    print(response)

    #Response
    """
    {
        "body": "Hello! This is Diptam",
        "num_segments": "1",
        "direction": "outbound-api",
        "from": "whatsapp:+14155238886",
        "date_updated": "Wed, 04 Jan 2023 14:09:46 +0000",
        "price": null,
        "error_message": null,
        "uri": "/2010-04-01/Accounts/AC1463d34872ec53122a2fb0dd7148521e/Messages/SM711900d2e4cd4ef690b4aca7cec525fe.json",
        "account_sid": "AC1463d34872ec53122a2fb0dd7148521e",
        "num_media": "0",
        "to": "whatsapp:+917699419499",
        "date_created": "Wed, 04 Jan 2023 14:09:46 +0000",
        "status": "queued",
        "sid": "SM711900d2e4cd4ef690b4aca7cec525fe",
        "date_sent": null,
        "messaging_service_sid": null,
        "error_code": null,
        "price_unit": null,
        "api_version": "2010-04-01",
        "subresource_uris": {
            "media": "/2010-04-01/Accounts/AC1463d34872ec53122a2fb0dd7148521e/Messages/SM711900d2e4cd4ef690b4aca7cec525fe/Media.json"
        }
    }
    """
    response_json = json.dumps(response)
    return response_json["sid"]