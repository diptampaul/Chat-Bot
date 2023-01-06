from django.http.response import HttpResponse, JsonResponse
from django.utils import timezone
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
import os
import logging
logger = logging.getLogger('django')
from dashboard.models import *
from main.models import *
from main.utils import *
from .utils import *

# Create your views here.
class SendToWhatsapp(APIView):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    """Usual Request Body Text -> <QueryDict: {'SmsMessageSid': ['SM257d0529a8938251516e56d5ec6ba46c'], 'NumMedia': ['0'], 'ProfileName': ['Diptam Paul'], 'SmsSid': ['SM257d0529a8938251516e56d5ec6ba46c'], 'WaId': ['fromNum'], 'SmsStatus': ['received'], 'Body': ['Hi'], 'To': ['whatsapp:+/'], 'NumSegments': ['1'], 'ReferralNumMedia': ['0'], 'MessageSid': ['SM257d0529a8938251516e56d5ec6ba46c'], 'AccountSid': ['AC1463d34872ec53122a2fb0dd7148521e'], 'From': ['whatsapp:+/'], 'ApiVersion': ['2010-04-01']}>
    
    Image -> <QueryDict: {'MediaContentType0': ['image/jpeg'], 'SmsMessageSid': ['MM258c7d2face97078418bc205b8683cf2'], 'NumMedia': ['1'], 'ProfileName': ['Diptam Paul'], 'SmsSid': ['MM258c7d2face97078418bc205b8683cf2'], 'WaId': ['fromNum'], 'SmsStatus': ['received'], 'Body': [''], 'To': ['whatsapp:+/'], 'NumSegments': ['1'], 'ReferralNumMedia': ['0'], 'MessageSid': ['MM258c7d2face97078418bc205b8683cf2'], 'AccountSid': ['AC1463d34872ec53122a2fb0dd7148521e'], 'From': ['whatsapp:+/'], 'MediaUrl0': ['https://api.twilio.com/2010-04-01/Accounts/AC1463d34872ec53122a2fb0dd7148521e/Messages/MM258c7d2face97078418bc205b8683cf2/Media/ME88ee37a8772f605eb9a588dca17b62ba'], 'ApiVersion': ['2010-04-01']}>"""

    def get(self, request):
        return HttpResponse("Get method not allowed", status=403)

    def post(self, request, *args, **kwargs):
        body = request.data.dict()
        sending_message = ""
        logger.info(body)
        phone_no = body["From"].split(":")[-1]
        name = body["ProfileName"]
        message_id = body["MessageSid"]
        message_status = body["SmsStatus"]
        try:
            message_type = body["MediaContentType0"]
            message_text = None
            media_link = str(body["MediaUrl0"])
        except:
            message_type = "Text"
            message_text = body["Body"]
            media_link = None
        logger.info(f"{phone_no} raised a message {message_text}")

        #Check exhistences
        profile_obj = Profile.objects.filter(phone_no = phone_no)
        if profile_obj:
            logger.info("Known User")
            #Check conversation time, if it is within 20 hours, reply normal, else starts with greeting
            conversation_obj = UserWPConversation.objects.filter(profile__phone_no = phone_no).order_by('-created_timestamp')
            logger.info("Time elapsed till the conversation started : " + (conversation_obj.created_timestamp - timezone.now()).total_seconds())
            if (conversation_obj.created_timestamp - timezone.now()).total_seconds() > 72000:
                sending_message += "```New conversation started... Chats older than 20 hours has been purged```\nHi !! This is Jahnbi AI at your service!! \n\n "
                conversation_obj = UserWPConversation(profile = profile_obj)
                conversation_obj.save()
                message_id = two_way_message(phone_no, sending_message)
                update_token_balance(profile_obj, message_id, sending_message, False)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
            
            #Add the received message to the conversation
            UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = message_text, media_link = media_link, message_status = message_status)

            #Check token balance, if below threshold show warning
            user_token_obj = UserTokenBalance.objects.filter(profile = profile_obj)
            if user_token_obj.tokens <= user_token_obj.token_threshold:
                sending_message = f"Seems like you have reached the token threshold. No worries. Buy tokens from _[URL]_ , starting as low as 50 Rs only. "
                message_id = two_way_message(phone_no, sending_message)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                update_token_balance(profile_obj, message_id, sending_message, False)
                return JsonResponse({'errorCode': 0, 'message': "Success",}, status=200)

            #Load diferent response for image and text messages
            if message_type != "Text":
                sending_message = f"I'm very sorry. I can't interpret visuals that don't have context. Please see my website for all of the hidden commands you may ask me."
                message_id = two_way_message(phone_no, sending_message)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                update_token_balance(profile_obj, message_id, sending_message, False)
            else:
                output = get_ai_answer(message_text)
                sending_message = output["text"]
                message_id = two_way_message(phone_no, sending_message)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                update_token_balance(profile_obj, message_id, sending_message, False)
                update_token_balance(profile_obj, message_id, message_text, False)
            

        else:
            logger.info("Unknown User")
            user_buffer_chats = UserBufferWPChat.objects.filter(phone_no = phone_no).order_by('-created_timestamp')
            if user_buffer_chats:
                logger.info("User already chatted")
                UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = message_type, message_text = message_text, media_link = media_link, message_status = message_status)

                #If asked for email address, verify and create profile
                if "@" in message_text and "." in message_text:
                    message_text = message_text.lower()
                    logger.info("User gave correct email address")
                    profile_obj = Profile.objects.filter(email=str(message_text))
                    if profile_obj:
                        sending_message = f"The email address is already in use. Please visit website/app to add this number with your email address or provide a different email address : "
                        message_id = two_way_message(phone_no, sending_message)
                        UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")
                        return JsonResponse({'errorCode': 0, 'message': "Success",}, status=200)
                    profile_obj = Profile(name=name, email=str(message_text), password =None, is_password_given = False, phone_no = phone_no)
                    profile_obj.save()
                    UserTokenBalance.objects.create(profile = profile_obj, tokens = 500.0)

                    sending_message = f"New Account has been successfully created at *Jahnbi AI - Your personal assistant.* You got 500 tokens for free. Please go to _[URL]_ to claim your free 5000 additional tokens. \n\n Hi {name}! \n\n I am your own knowledge assistant / private wiki *Jahnbi*. You can ask me anything you want, and I will try my best to answer each questions. I can also create AI art, just ask /ART at any time. \n\n ```Visit website/app to know more about secret commands which can unlock some special feature of Jahnbi. All chats with Jahnbi is end to end encrypted and removed after 20 hours```"
                    message_id = two_way_message(phone_no, sending_message)
                    UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")

                    #Move all chats to USERWPCHAT
                    all_chats = UserBufferWPChat.objects.filter(phone_no = phone_no)
                    conversation = UserWPConversation(profile = profile_obj, created_timestamp = timezone.now())
                    conversation.save()
                    for chat in all_chats:
                        UserWPChat.objects.create(conversation = conversation, message_id = chat.message_id, message_type = chat.message_type, message_text = chat.message_text, media_link = chat.media_link, message_status = chat.message_status)
                        chat.delete()

                else:
                    logger.info("User gave invalid email address")
                    sending_message = f"Hmm... Didn't seems like a valid Email \n Please enter a valid email id : "
                    message_id = two_way_message(phone_no, sending_message)
                    UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")
            else:
                logger.info("First time user")
                #Ask for email addresses
                UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = message_type, message_text = message_text, media_link = media_link, message_status = message_status)

                sending_message ="Sorry! I've never met you. Next, please provide your email address : "
                message_id = two_way_message(phone_no, sending_message)
                UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")

        logger.info(f"{phone_no} received a message {sending_message}")
        return JsonResponse({'errorCode': 0, 'message': "Success",}, status=200)

class WhatsappCallbackView(APIView):
    """{'SmsSid': 'SM4113ee4567acd2ccda59bfe5933ef837', 'SmsStatus': 'delivered', 'MessageStatus': 'delivered', 'ChannelToAddress': '+91769941XXXX', 'To': 'whatsapp:+917699419499', 'ChannelPrefix': 'whatsapp', 'MessageSid': 'SM4113ee4567acd2ccda59bfe5933ef837', 'AccountSid': 'AC1463d34872ec53122a2fb0dd7148521e', 'From': 'whatsapp:+14155238886', 'ApiVersion': '2010-04-01', 'ChannelInstallSid': 'XEd6f617b8ab42381914bdd75304dccb6e'}"""

    def get(self, request):
        return HttpResponse("Get method not allowed", status=403)

    def post(self, request, *args, **kwargs):
        body = request.data.dict()
        sending_message = ""
        logger.info(body)
        return JsonResponse(
                    {
                        'errorCode': 0,
                        'message': "Success",
                    }, status=200)