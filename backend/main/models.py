from django.db import models
from django.core.validators import URLValidator
from dashboard.models import Profile

# Create your models here.
class UserWPConversation(models.Model):
    profile = models.ForeignKey(Profile, to_field='user_id', on_delete=models.CASCADE)
    conversation_id = models.AutoField(primary_key=True)
    created_timestamp = models.DateTimeField(blank=False, auto_now_add=True)

class UserWPChat(models.Model):
    conversation = models.ForeignKey(UserWPConversation, to_field='conversation_id', on_delete=models.CASCADE)
    message_id = models.CharField(max_length=100)
    message_type = models.CharField(max_length=50)
    message_text = models.TextField(blank=True, null=True)
    media_link = models.TextField(validators=[URLValidator()], blank=True, null=True)
    message_status = models.CharField(max_length=10)  #Sent or received or failed
    created_timestamp = models.DateTimeField(blank=False, auto_now_add=True)
