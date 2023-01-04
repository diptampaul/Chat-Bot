from django.db import models

# Create your models here.
class Profile(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=20)
    created_timestamp = models.DateTimeField(blank=False, auto_now_add=True)

class UserTokenBalance(models.Model):
    profile = models.ForeignKey(Profile, to_field='user_id', on_delete=models.CASCADE)
    tokens = models.DecimalField(max_digits=20, decimal_places=7)

class EachTokenMap(models.Model):
    token = models.PositiveIntegerField(default=1)
    other_character = models.DecimalField(max_digits=10, decimal_places=7, default=1)
    whatsapp_character = models.DecimalField(max_digits=10, decimal_places=7,default=0.6)
    image = models.DecimalField(max_digits=10, decimal_places=7, default=0.00025)

class TokenUsage(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, to_field='user_id', on_delete=models.CASCADE)
    token_used = models.DecimalField(max_digits=20, decimal_places=7)
    used_paltform = models.CharField(max_length=20)
    message_id = models.CharField(max_length=100)
