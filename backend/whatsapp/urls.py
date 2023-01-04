from django.urls import path
from . import views


urlpatterns = [
    path('',views.SendToWhatsapp.as_view(), name='send_to_whatsapp'),
    path('callback/',views.WhatsappCallbackView.as_view(), name='whatsapp_callback'),
]