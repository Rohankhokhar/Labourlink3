from django.conf import settings

from twilio.rest import Client

import os

def send_sms(data):
    print(data)
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    sms_twilio_client = Client(account_sid, auth_token)

    message = sms_twilio_client.messages.create(
                              from_= settings.TWILIO_MOBILE_NUMBER,
                              body=data['message'],
                              to=data['to_mobile_number'])
    print(message)
    return message
