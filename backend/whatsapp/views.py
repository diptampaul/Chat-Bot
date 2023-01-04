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
from .models import *
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
        
        return JsonResponse(
                    {
                        'errorCode': 0,
                        'message': "Success",
                    }, status=202)

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