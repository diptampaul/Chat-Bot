from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(OpenAIAnswer)
admin.site.register(StableDiffusionImageGeneration)
admin.site.register(UserBufferWPChat)
admin.site.register(UserWPConversation)
admin.site.register(UserWPChat)