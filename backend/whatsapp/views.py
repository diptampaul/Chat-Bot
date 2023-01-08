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
            profile_obj = profile_obj[0]
            logger.info("Known User")
            #Check conversation time, if it is within 20 hours, reply normal, else starts with greeting
            conversation_obj = UserWPConversation.objects.filter(profile__phone_no = phone_no).order_by('-created_timestamp')[0]
            logger.info("Time elapsed till the conversation started : " + str((conversation_obj.created_timestamp - timezone.now()).total_seconds()))
            if (conversation_obj.created_timestamp - timezone.now()).total_seconds() > 72000:
                logger.info("New conversation started")
                sending_message += "```New conversation started... Chats older than 20 hours has been purged```\nHi !! This is Jahnbi AI at your service!! \n\n "
                conversation_obj = UserWPConversation(profile = profile_obj)
                conversation_obj.save()
                message_id = two_way_message(phone_no, sending_message)
                update_token_balance(profile_obj, phone_no, message_id, sending_message, False)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
            
            #Add the received message to the conversation
            UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = message_text, media_link = media_link, message_status = message_status)

            #Check token balance, if below threshold show warning
            user_token_obj = UserTokenBalance.objects.get(profile__phone_no = phone_no)
            if user_token_obj.tokens <= user_token_obj.token_threshold:
                logger.info("Token balance below threshold")
                sending_message = f"Seems like you have reached the token threshold. No worries. Buy tokens from _[URL]_ , starting as low as 50 Rs only. "
                message_id = two_way_message(phone_no, sending_message)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                update_token_balance(profile_obj, phone_no, message_id, sending_message, False)
                return JsonResponse({'errorCode': 0, 'message': "Success",}, status=200)

            #Load diferent response for image and text messages
            if message_type != "Text":
                logger.info("Other media types came")
                logger.info(message_text)
                logger.info(media_link)
                sending_message = f"I'm very sorry. I can't interpret visuals that don't have context. Please see my website for all of the hidden commands you may ask me."
                message_id = two_way_message(phone_no, sending_message)
                UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                update_token_balance(profile_obj, phone_no, message_id, sending_message, False)

            else:
                logger.info("Text message came")
                max_token_per_chat = user_token_obj.max_token_per_chat / 4 if user_token_obj.max_token_per_chat < 600 else user_token_obj.max_token_per_chat / 5 
                logger.info(f"Max token per chat {max_token_per_chat}")
                message_text = message_text.lower()

                #For AI Image check
                if "/image " in message_text and "image" in message_text:
                    number_of_images = int(user_token_obj.number_of_image) if user_token_obj.number_of_image <= 10 else int(10) 
                    #If the remaining token is less than 4600, don't do    
                    if user_token_obj.tokens <= (4600*number_of_images):
                        logger.info("AI Image cannot be generated because of insufficient tokens")
                        sending_message = f"Hey, you don't have enough tokens to generate AI images. Please have atleast 5000 tokens to generate single AI images or buy our special package for AI images. And if required change number of images will be generated per chat from your profile. You can ask */settings* to see current settings. Visit :  _[URL]_ to recharge"
                        message_id = two_way_message(phone_no, sending_message)
                        UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                        update_token_balance(profile_obj, phone_no, message_id, sending_message, False)
                        return JsonResponse({'errorCode': 0, 'message': "Success",}, status=200)

                    update_token_balance(profile_obj, phone_no, message_id, message_text, True)
                    message_text = message_text.split("/image ")[-1]
                    image_size = int(user_token_obj.image_size)
                    if image_size > 200 and image_size <= 500:
                        token_used = 3000
                    elif image_size > 500 and image_size <= 1000:
                        token_used = 3600
                    else:
                        token_used = 4000
                    logger.info("AI generating AI Image")
                    image_datas = get_ai_image(message_id = message_id, prompt=message_text, image_size=image_size, number_of_images = number_of_images)
                    logger.info(image_datas)
                    for image_data in image_datas:
                        message_id = send_image(phone_no, image_data["image_url"])
                        UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = None, media_link = image_data["image_url"], message_status = "sent")
                        update_token_balance_for_image(profile_obj, phone_no, message_id, token_used)

                #For other than AI Image
                else:
                    if "/code" in message_text:
                        message_text = message_text.split("/code ")[-1]
                        message_text = "Write a program on " + message_text
                        output = get_ai_answer(message_text, int(max_token_per_chat))
                        sending_message = output["text"]
                        update_token_balance(profile_obj, phone_no, message_id, message_text, True)

                    elif "/setting" in message_text or "/settings" in message_text:
                        password = "Secure" if profile_obj.is_password_given() else "Not Set"
                        sending_message = f"Hi! Below is the details of your profile. To Update any details, kindly visit _[URL]_ or app to change the settings. \n\n ↳ Email : {profile_obj.email} \n ↳ Password : {password} \n ↳ Phone Number : {phone_no} \n\n Token Details - \n ↳ Available Tokens : {user_token_obj.tokens} \n ↳ Maximum Tokens used per Chat : {user_token_obj.max_token_per_chat} \n ↳ Token Threshold : {user_token_obj.token_threshold} \n\n AI Images Details - \n ↳ Number of images to be generated : {user_token_obj.number_of_image} \n ↳ Image Size : {user_token_obj.image_size}x{user_token_obj.image_size}"

                    elif "/help" in message_text:
                        pass

                    #Basic introduction
                    elif message_text.lower() in ["who are you", "who are you?",  "what is your name", "what is your name?", "tell me about you", "tell me about yourself"]:
                        sending_message = whoami_reponse()
                    #Basic Hi Hello reponse
                    elif message_text.lower() in ["hi", "hello", "namaskar", "hola!"]:
                        sending_message = greetings()

                    else:   
                        logger.info("Ai generating Chat reponse")
                        if "chat" in message_text and "/chat " in message_text:
                            message_text = message_text.split("/chat ")[-1]
                            output = get_ai_answer(message_text, int(max_token_per_chat))
                            sending_message = output["text"]
                            update_token_balance(profile_obj, phone_no, message_id, message_text, True)
                        elif "/" in message_text:
                            command = message_text.split("/")[-1].split(" ")[0]
                            sending_message = f"Command {command} is not recognized. Write /help or visit website to learn more about secret commands."
                        else:
                            output = get_ai_answer(message_text, int(max_token_per_chat))
                            sending_message = output["text"]
                            update_token_balance(profile_obj, phone_no, message_id, message_text, True)

                    message_id = two_way_message(phone_no, sending_message)
                    UserWPChat.objects.create(conversation = conversation_obj, message_id = message_id, message_type = message_type, message_text = sending_message, media_link = media_link, message_status = "sent")
                    update_token_balance(profile_obj, phone_no, message_id, sending_message, True)
        

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

                    #Create new profile    
                    profile_obj = Profile(name=name, email=str(message_text), password =None, is_password_given = False, phone_no = phone_no)
                    profile_obj.save()
                    UserTokenBalance.objects.create(profile = profile_obj, tokens = 1000.0)

                    sending_message = f"New Account has been successfully created at *Jahnbi AI - Your personal assistant.* You got 1000 tokens for free. Please go to _[URL]_ to claim your free 5000 additional tokens. \n\n Hi {name}! \n\n I am your own knowledge assistant / private wiki *Jahnbi*. You can ask me anything you want, and I will try my best to answer each questions. I can also create AI art, just ask /ART at any time. \n\n ```Visit website/app to know more about secret commands which can unlock some special feature of Jahnbi. All chats with Jahnbi is end to end encrypted and removed after 20 hours```"
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