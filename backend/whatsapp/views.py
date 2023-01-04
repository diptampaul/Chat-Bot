from django.http.response import HttpResponse, JsonResponse
from django.utils import timezone
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from dashboard.models import Profile, UserLogin
import os
import logging
import json
logger = logging.getLogger('django')

# Create your views here.
class HomeView(APIView):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get(self, request):
        return HttpResponse("Welcome !! Diptam Bonds")