from django.conf import settings
from twilio.rest import Client 
from dashboard.models import *
import random

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

def send_image(sender_number, media_link):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
         media_url=[media_link],
         from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
         to=f'whatsapp:{sender_number}'
     )
    
    response = message.sid
    return response


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
    return response

def update_token_balance(profile_obj, phone_no, message_id, messsage, open_ai_used = True):
    total_tokens_used = len(messsage)
    token_converter = EachTokenMap.objects.get(token = 1).whatsapp_character if open_ai_used else EachTokenMap.objects.get(token = 1).other_character
    total_tokens_used = total_tokens_used * token_converter

    user_token_obj = UserTokenBalance.objects.get(profile__phone_no = phone_no)
    remaining_tokens = user_token_obj.tokens - total_tokens_used
    user_token_obj.tokens = remaining_tokens
    user_token_obj.save()
    TokenUsage.objects.create(profile = profile_obj, token_used = total_tokens_used, remaining_tokens = remaining_tokens, used_paltform = "WhatsApp Chat", message_id = message_id)

def update_token_balance_for_image(profile_obj, phone_no, message_id, image_cost):
    total_tokens_used = int(image_cost)

    user_token_obj = UserTokenBalance.objects.get(profile__phone_no = phone_no)
    remaining_tokens = user_token_obj.tokens - total_tokens_used
    user_token_obj.tokens = remaining_tokens
    user_token_obj.save()
    TokenUsage.objects.create(profile = profile_obj, token_used = total_tokens_used, remaining_tokens = remaining_tokens, used_paltform = "WhatsApp Chat", message_id = message_id)


def whoami_reponse():
    return random.choice(["I am your personal assistant. My major role is to aid users in creating human-like language depending on the input supplied to me. I have no personal experiences or sentiments, and I am not a person, but rather a software created to deliver information and answer inquiries to the best of my abilities. Is there anything else you'd want to know?", "I am your personal assistant. My primary role is to aid users in creating human-like writing from the input supplied to me. I have no personal sentiments or experiences, and I am not a person, but rather a software created to deliver information and answer inquiries to the best of my abilities. Is there anything more I can tell you?", "As a language model, I was designed to generate human-like text based on the input provided to me. I do not have personal experiences or feelings and am not a person, but rather a program. I was trained on a dataset of billions of words and can answer questions on a wide range of topics, including but not limited to general knowledge, mathematics, science, history, and more. My primary function is to assist users in generating human-like text, and I do not have the ability to browse the internet or access new information beyond what I was trained on. Is there anything else you would like to know?", "I was created as a language model to generate human-like prose based on the input given to me. I have no personal experiences or sentiments, and I am a software rather than a person. I was trained on a billion-word dataset and can answer questions about a wide range of topics, including but not limited to general knowledge, mathematics, physics, history, and others. My major role is to aid people in producing human-like text, and I am unable to explore the internet or obtain new knowledge beyond what I was taught on. Is there anything more I should know?"])