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
import json
logger = logging.getLogger('django')
from dashboard.models import *
from main.models import *
from .utils import *

# Create your views here.
class SendToWhatsapp(APIView):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    """Usual Request Body Text -> <QueryDict: {'SmsMessageSid': ['SM257d0529a8938251516e56d5ec6ba46c'], 'NumMedia': ['0'], 'ProfileName': ['Diptam Paul'], 'SmsSid': ['SM257d0529a8938251516e56d5ec6ba46c'], 'WaId': ['fromNum'], 'SmsStatus': ['received'], 'Body': ['Hi'], 'To': ['whatsapp:+/'], 'NumSegments': ['1'], 'ReferralNumMedia': ['0'], 'MessageSid': ['SM257d0529a8938251516e56d5ec6ba46c'], 'AccountSid': ['AC1463d34872ec53122a2fb0dd7148521e'], 'From': ['whatsapp:+/'], 'ApiVersion': ['2010-04-01']}>
    
    Image -> <QueryDict: {'MediaContentType0': ['image/jpeg'], 'SmsMessageSid': ['MM258c7d2face97078418bc205b8683cf2'], 'NumMedia': ['1'], 'ProfileName': ['Diptam Paul'], 'SmsSid': ['MM258c7d2face97078418bc205b8683cf2'], 'WaId': ['fromNum'], 'SmsStatus': ['received'], 'Body': [''], 'To': ['whatsapp:+/'], 'NumSegments': ['1'], 'ReferralNumMedia': ['0'], 'MessageSid': ['MM258c7d2face97078418bc205b8683cf2'], 'AccountSid': ['AC1463d34872ec53122a2fb0dd7148521e'], 'From': ['whatsapp:+/'], 'MediaUrl0': ['https://api.twilio.com/2010-04-01/Accounts/AC1463d34872ec53122a2fb0dd7148521e/Messages/MM258c7d2face97078418bc205b8683cf2/Media/ME88ee37a8772f605eb9a588dca17b62ba'], 'ApiVersion': ['2010-04-01']}>"""

    def get(self, request):
        return HttpResponse("Get method not allowed", status=403)

    def post(self, request, *args, **kwargs):
        body = json.dumps(request.data)
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

        #Check exhistences
        profile_obj = Profile.objects.filter(phone_no = phone_no)
        if profile_obj:
            pass

        else:
            user_buffer_chats = UserBufferWPChat.objects.filter(phone_no = phone_no).order_by('-created_timestamp')
            if user_buffer_chats:
                UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = message_type, message_text = message_text, media_link = media_link, message_status = message_status)

                #If asked for email address, verify and create profile
                last_message = user_buffer_chats[0].message_text
                if last_message == "Sorry! I've never met you. Next, please provide your email address : ":
                    if "@" in message_text and "." in message_text:
                        profile_obj = Profile(name=name, email=str(message_text), password =None, is_password_given = False, phone_no = phone_no)
                        profile_obj.save()
                        UserTokenBalance(profile = profile_obj, tokens = 500.0)

                        sending_message = f"New Account has been successfully created at *Jahnbi AI - Your personal assistant.* You got 500 tokens. Please go to _https://jahnbi.com_ to claim your free 5000 additional tokens. \n\n Hi {name}! \n\n I am your own knowledge assistant / private wiki *Jahnbi*. You can ask me anything you want, and I will give proper and short answer to each question. I can also create AI art, just ask /ART at any time. \n\n ```Visit website/app to know more about secret commands which can unlock some special feature of Jahnbi. All chats with Jahnbi is end to end encrypted```"
                        message_id = two_way_message(phone_no, sending_message)
                        UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")

                        #Move all chats to USERWPCHAT
                        all_chats = UserBufferWPChat.objects.filter(phone_no = phone_no)
                        conversation = UserWPConversation(profile_obj)
                        conversation.save()
                        for chat in all_chats:
                            UserWPChat.objects.create(conversation = conversation, message_id = chat.message_id, message_type = chat.message_type, message_text = chat.message_text, media_link = chat.media_link, message_status = chat.message_status)

                    else:
                        sending_message = f"Hmm... Didn't seems like a valid Email \n Please enter a valid email id : "
                        message_id = two_way_message(phone_no, sending_message)
                        UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")
            else:
                #Ask for email addresses
                UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = message_type, message_text = message_text, media_link = media_link, message_status = message_status)

                sending_message ="Sorry! I've never met you. Next, please provide your email address : "
                message_id = two_way_message(phone_no, sending_message)
                UserBufferWPChat.objects.create(phone_no = phone_no, message_id = message_id, message_type = "Text", message_text = sending_message, media_link = None, message_status = "sent")

        return JsonResponse(
                {
                    'errorCode': 0,
                    'message': "Success",
                }, status=200)

class WhatsappCallbackView(APIView):

    def get(self, request):
        return HttpResponse("Get method not allowed", status=403)

    def post(self, request, *args, **kwargs):
        body = request.POST.get('body')
        logger.info(body)
        return JsonResponse(
                    {
                        'errorCode': 0,
                        'message': "Success",
                    }, status=202)