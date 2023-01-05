from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(UserTokenBalance)
admin.site.register(TokenUsage)
admin.site.register(EachTokenMap)